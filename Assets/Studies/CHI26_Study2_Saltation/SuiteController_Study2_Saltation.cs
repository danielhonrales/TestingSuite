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

    public override TrialInfo CreateTrialInfo(string data)
    {
        return new TrialInfo_Study2_Saltation(data);
    }

    public override void SaveTrialResponse(string[] responseParams)
    {
        string[] responseArray = PadResponseArray(responseParams, 4);
        int responseParticipantNumber = int.Parse(responseArray[0]);
        int responseTrialNumber = int.Parse(responseArray[1]);
        string locationsString = responseArray[2];
        List<float> locations = ParseLocations(locationsString);
        string thermalsString = responseArray[3];
        List<string> thermals = ParseThermals(thermalsString);

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
                writer.WriteLine("participantNumber,trialNumber,locations,thermals");
            }
            writer.WriteLine($"{responseParticipantNumber},{responseTrialNumber},{string.Join(",", locations)},{string.Join(",", thermals)}");
        }
        Console.WriteLine($"Wrote trial {responseTrialNumber} to CSV.");
    }

    private List<float> ParseLocations(string locationsString)
    {
        return locationsString
            .Trim('[', ']')                  // remove [ and ]
            .Split('|')                      // split by comma
            .Select(s => float.Parse(s.Trim())) // remove spaces and quotes
            .ToList();
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
