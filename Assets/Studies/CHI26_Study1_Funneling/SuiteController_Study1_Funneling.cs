using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using TMPro;
using UnityEditor.VersionControl;
using UnityEngine;
using UnityEngine.UI;

public class SuiteController_Study1_Funneling : SuiteController
{

    public TMP_InputField inputDuration;
    public TMP_InputField inputLocation;

    public override TrialInfo CreateTrialInfo(string data)
    {
        return new TrialInfo_Study1_Funneling(data);
    }

    public override void SaveTrialResponse(string[] responseParams)
    {
        string[] responseArray = PadResponseArray(responseParams, 2 + 3);
        int responseParticipantNumber = int.Parse(responseArray[0]);
        int responseTrialNumber = int.Parse(responseArray[1]);
        string feltThermal = responseArray[2];
        string feltLocation = responseArray[3];

        string filePath = string.Format("{0}\\trial_responses\\p{1}_response.csv", studyFolder, responseParticipantNumber);
        string directory = Path.GetDirectoryName(filePath);
        if (!Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }
        bool fileExists = File.Exists(filePath);

        using (StreamWriter writer = new(filePath, append: true, Encoding.UTF8))
        {
            if (!fileExists)
            {
                writer.WriteLine("participantNumber,trialNumber,feltThermal,feltLocation");
            }
            writer.WriteLine($"{responseParticipantNumber},{responseTrialNumber},{feltThermal},{feltLocation}");
        }
        Console.WriteLine($"Wrote trial {responseTrialNumber} to CSV.");
    }

    public void SendTestMessage()
    {
        TrialInfo_Study1_Funneling testTrialInfo = new("0,9,1,0.5");
        testTrialInfo.duration = float.Parse(inputDuration.text);
        testTrialInfo.location = float.Parse(inputLocation.text);
        string message = JsonUtility.ToJson(new PiMessage_Study1_Funneling(baseTemp + testTrialInfo.temperature, testTrialInfo, overrideHotVoltage));
        communicationController.SendMessageToPi(message);
    }
}
