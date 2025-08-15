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

public class SuiteController_Study1_Funneling : SuiteController
{

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
}
