using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using NUnit.Framework.Internal;
using UnityEngine;
using UnityEngine.UI;

public class CommunicationController : MonoBehaviour
{

    [Space(10)]
    [Header("Pi Connection")]
    public string piIP = "172.16.136.241";
    public int piPort = 25567;
    public TcpClient piClient;
    public NetworkStream piStream;

    [Space(10)]
    [Header("Response Tool Connection")]
    public string suiteIP = "172.16.136.202";
    public int hostingPort = 25568;
    public TcpClient toolClient;
    public TcpListener toolListener;
    public NetworkStream toolStream;
    private Thread toolListenerThread;

    [Space(10)]
    [Header("References")]
    public SuiteController suiteController;
    public Image piConnectButton;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        toolListenerThread = new Thread(new ThreadStart(ListenForResponseToolConnection)){IsBackground = true};
        toolListenerThread.Start();
    }

    // Update is called once per frame
    void Update()
    {

    }

    public void ConnectToPi()
    {
        try
        {
            // Create a TCP/IP socket
            piClient = new TcpClient();
            if (!piClient.ConnectAsync(piIP, piPort).Wait(2000))
            {
                Debug.Log("Pi connection timeout");
                SocketError(new SocketException(), piConnectButton);
            }

            // Get a client stream for reading and writing
            piStream = piClient.GetStream();

            Debug.Log("SignalSender is connected");
            piConnectButton.color = Color.green;
        }
        catch (SocketException e)
        {
            SocketError(e, piConnectButton);
        }
    }

    public void SendMessageToPi(string message)
    {
        Debug.Log("Sending message to Pi: " + message);
        SendMessage(message, piStream);
    }

    public void SendMessage(string message, NetworkStream stream)
    {
        int packetSize = 4096;

        try
        {
            // Translate the signal string into bytes
            byte[] data = Encoding.ASCII.GetBytes(message + "$");

            // Send message count
            int packetCount = (int)Math.Ceiling((float)data.Length / packetSize);
            byte[] countData = Encoding.ASCII.GetBytes(packetCount.ToString());

            // Send messages
            for (int i = 0; i < packetCount; i++)
            {
                int start = i * packetSize;
                int end = Math.Min((i + 1) * packetSize, data.Length);
                int length = end - start;
                stream.Write(data, start, length);
            }
            Debug.Log("Message sent");

        }
        catch (Exception e)
        {
            if (stream == piStream)
            {
                SocketError(e, piConnectButton);
            }
        }
    }

    public void ListenForResponseToolConnection()
    {
        try
        {
            // Create listener on localhost port 8052. 			
            toolListener = new TcpListener(IPAddress.Parse(suiteIP), hostingPort);
            toolListener.Start();
            Debug.Log("TestingSuite is listening for tool conenction");
            while (true)
            {
                toolClient = toolListener.AcceptTcpClient();
                toolStream = toolClient.GetStream();
                ReceiveMessageFromTool();
            }
        }
        catch (SocketException socketException)
        {
            Debug.Log("SocketException " + socketException.ToString());
        }
    }

    public void SendMessageToResponseTool(string message)
    {
        Debug.Log("Sending message to tool: " + message);
        SendMessage(message, toolStream);
    }

    public void ReceiveMessageFromTool()
    {
        int length;
        byte[] bytes = new byte[4096];
        // Read incomming stream into byte arrary. 						
        while ((length = toolStream.Read(bytes, 0, bytes.Length)) != 0)
        {
            var incommingData = new byte[length];
            Array.Copy(bytes, 0, incommingData, 0, length);
            string messageFromTool = Encoding.ASCII.GetString(incommingData);
            Debug.Log("Received message from Tool: " + messageFromTool);

            suiteController.HandleMessageFromTool(messageFromTool);
        }
    }

    private void SocketError(Exception e, Image button)
    {
        Debug.Log("Socket Exception: " + e);
        button.color = Color.red;
    }
}
