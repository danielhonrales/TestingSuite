using System;
using System.Collections.Generic;
using UnityEngine;


public class TrialInfo_Study1_Funneling : TrialInfo
{

    // Factors
    public int temperature;
    public float location;

    public TrialInfo_Study1_Funneling(string rawInfo) : base(rawInfo)
    {
        string[] info = rawInfo.Split(',');
        this.temperature = int.Parse(info[1]);
        this.duration = float.Parse(info[2]);
        this.location = float.Parse(info[3]);
    }

    public override string GetPiMessage(int baseTemp)
    {
        return JsonUtility.ToJson(new PiMessage_Study1_Funneling(baseTemp + temperature, this));
    }
}

public class PiMessage_Study1_Funneling
{
    public string illusion;
    public double thermalVoltage;
    public float duration;
    public float location;

    public PiMessage_Study1_Funneling(int targetTemp, TrialInfo_Study1_Funneling trialInfo)
    {
        illusion = "funneling";
        thermalVoltage = Math.Round(ThermalVoltageMapping.targetTempToVoltMapping[targetTemp], 1);
        duration = trialInfo.duration;
        location = trialInfo.location;
    }
}