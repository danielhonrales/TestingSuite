using System;
using System.Collections.Generic;
using UnityEngine;


public class TrialInfo_Study2_Saltation : TrialInfo
{

    // Factors
    public int temperature;
    public int direction;

    public TrialInfo_Study2_Saltation(string rawInfo) : base(rawInfo)
    {
        string[] info = rawInfo.Split(',');
        this.temperature = int.Parse(info[1]);
        this.duration = float.Parse(info[2]);
        this.direction = int.Parse(info[3]);
    }

    public override string GetPiMessage(int baseTemp, float overrideHotVoltage)
    {
        return JsonUtility.ToJson(new PiMessage_Study2_Saltation(baseTemp + temperature, this, overrideHotVoltage));
    }
}

public class PiMessage_Study2_Saltation
{
    public string illusion;
    public double thermalVoltage;
    public float duration;
    public int direction;

    public PiMessage_Study2_Saltation(int targetTemp, TrialInfo_Study2_Saltation trialInfo, float overrideHotVoltage = 0)
    {
        illusion = "saltation";
        thermalVoltage = Math.Round(ThermalVoltageMapping.targetTempToVoltMapping[targetTemp], 1);
        if (overrideHotVoltage != 0 && targetTemp > 34)
        {
            thermalVoltage = Math.Min(overrideHotVoltage, 2);
        }
        duration = trialInfo.duration;
        direction = trialInfo.direction;
    }
}