using System;
using System.Collections.Generic;
using UnityEngine;


public class TrialInfo_Study2_Saltation
{
    public string rawInfo;

    // Factors
    public int temperature;
    public float duration;
    public float location;

    public TrialInfo_Study2_Saltation(string rawInfo)
    {
        this.rawInfo = rawInfo;

        string[] info = rawInfo.Split(',');
        this.temperature = int.Parse(info[1]);
        this.duration = float.Parse(info[2]);
        this.location = float.Parse(info[3]);
    }

    public string GetPiMessage()
    {
        return JsonUtility.ToJson(new PiMessage_Study2_Saltation(this));
    }
}

public class PiMessage_Study2_Saltation
{
    public string illusion;
    public double thermalVoltage;
    public float duration;
    public float location;

    public PiMessage_Study2_Saltation(TrialInfo_Study2_Saltation trialInfo)
    {
        illusion = "funneling";
        thermalVoltage = Math.Round(ThermalVoltageMapping.mapping[trialInfo.temperature], 1);
        duration = trialInfo.duration;
        location = trialInfo.location;
    }
}