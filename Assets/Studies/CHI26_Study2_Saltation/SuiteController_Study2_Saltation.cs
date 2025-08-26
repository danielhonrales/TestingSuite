using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class SuiteController_Study2_Saltation : SuiteController
{

    public TMP_InputField inputDuration;
    public TMP_InputField inputDirection;

    public override TrialInfo CreateTrialInfo(string data)
    {
        return new TrialInfo_Study2_Saltation(data);
    }

    public override void SaveTrialResponse(string[] responseParams)
    {
        string[] responseArray = responseParams;
        int responseParticipantNumber = int.Parse(responseArray[0]);
        int responseTrialNumber = int.Parse(responseArray[1]);
        int feltThermal = int.Parse(responseArray[2]);
        int numberOfLocations = int.Parse(responseArray[3]);
        List<float> locations = new();

        for (int i = 0; i < numberOfLocations; i++)
        {
            locations.Add(float.Parse(responseArray[4 + i]));
        }

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
                writer.WriteLine("participantNumber,trialNumber,feltThermal,numberOfLocations,location1,location2,location3,extraLocations");
            }
            string line = $"{responseParticipantNumber},{responseTrialNumber},{feltThermal},{numberOfLocations}";
            for (int i = 0; i < locations.Count; i++)
            {
                line += $",{locations[i]}";
            }
            writer.WriteLine(line);
        }
        Console.WriteLine($"Wrote trial {responseTrialNumber} to CSV.");
    }

    public void SendTestMessage()
    {
        TrialInfo_Study2_Saltation testTrialInfo = new("0,9,.25,0");
        testTrialInfo.duration = float.Parse(inputDuration.text);
        testTrialInfo.direction = int.Parse(inputDirection.text);
        string message = JsonUtility.ToJson(new PiMessage_Study2_Saltation(baseTemp + testTrialInfo.temperature, testTrialInfo, overrideHotVoltage));
        communicationController.SendMessageToPi(message);
    }

    private List<string> ParseLocations(string locationsString)
    {
        return locationsString
            .Trim('[', ']')                  // remove [ and ]
            .Split('|')                      // split by comma
            .Select(s => s.Trim()) // remove spaces and quotes
            .ToList();
    }

    private List<string> PadLocations(List<string> locations)
    {
        while (locations.Count < 3)
        {
            locations.Add("");
        }
        return locations;
    }

    private List<string> ClearLocations(List<string> locations)
    {
        if (locations.Count > 3)
        {
            return new List<string> { "", "", "" };
        }
        return locations;
    }

    private List<string> ParseThermals(string thermalsString)
    {
        return thermalsString
            .Trim('[', ']')                  // remove [ and ]
            .Split('|')                      // split by comma
            .Select(s => s.Trim().Trim('"')) // remove spaces and quotes
            .ToList();
    }
}
