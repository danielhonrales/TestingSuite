using System;
using System.Collections.Generic;
using UnityEngine;


public class TrialInfo
{
    public string rawInfo;

    // Factors
    public int temperature;
    public float duration;
    public float location;

    public TrialInfo(string rawInfo)
    {
        this.rawInfo = rawInfo;

        string[] info = rawInfo.Split(',');
        this.temperature = int.Parse(info[1]);
        this.duration = float.Parse(info[2]);
        this.location = float.Parse(info[3]);
    }

    public string GetPiMessage()
    {
        return JsonUtility.ToJson(new PiMessage(this));
    }
}

public class PiMessage
{
    public string illusion;
    public double thermalVoltage;
    public float duration;
    public float location;

    public PiMessage(TrialInfo trialInfo)
    {
        illusion = "funneling";
        thermalVoltage = Math.Round(ThermalVoltageMapping.mapping[trialInfo.temperature], 1);
        duration = trialInfo.duration;
        location = trialInfo.location;
    }
}