#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "VM837614-2G";
const char* password = "jwwdxwfq";
const char* mqtt_server = "192.168.0.10";
char msg[20];

/* create an instance of PubSubClient client */
WiFiClient espClient;
PubSubClient client(espClient);

/*LED GPIO pin*/
const char led = 23;
/* topics */
#define TEMP_TOPIC    "floor1/room1/temp1"
#define LED_TOPIC     "floor1/room1/led1" /* on, off */

void setup_wifi()
{
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  
}

void setup_mqtt() 
{
  while (!client.connected()) 
  {
    Serial.print("MQTT connecting ...");
    if (client.connect("ESP32Client")) 
    {
      Serial.println("connected");
      client.subscribe(LED_TOPIC);
      client.subscribe(TEMP_TOPIC);
      Serial.println("----------------------------------");
    } 
    else 
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void receivedCallback(char* topic, byte* payload, unsigned int length) 
{
  Serial.print("topic: ");
  Serial.println(topic);
  
  if(strcmp(topic, LED_TOPIC) == 0)
  {
    Serial.print("payload: ");
    for (int i = 0; i < length; i++)
    {
      Serial.print((char)payload[i]);
    }
    Serial.println();
    /* we got '1' -> on */
    if ((char)payload[0] == '1') 
    {
      digitalWrite(led, HIGH); 
      snprintf (msg, 20, "%s", "on");
      /* publish the response */
      client.publish(LED_TOPIC "/res", msg);
    } 
    else 
    {
      /* we got '0' -> on */
      digitalWrite(led, LOW);
      snprintf (msg, 20, "%s", "off");
      client.publish(LED_TOPIC "/res", msg);
    }
  }
  else      
  {
    snprintf (msg, 20, "%d", random(0, 40));
    client.publish(TEMP_TOPIC "/res", msg);
  }
}

void setup() 
{
  Serial.begin(115200);
  pinMode(led, OUTPUT);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(receivedCallback);
}

void loop() 
{
  /* this function will listen for incomming 
  subscribed topic-process-invoke receivedCallback */
  client.loop();
  /* if client was disconnected then try to reconnect again */
  if (!client.connected()) 
  {
    digitalWrite(led, LOW);
    setup_mqtt();
  } 
}
