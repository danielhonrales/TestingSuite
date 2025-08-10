using System;
using System.Collections.Generic;
using UnityEngine;


public class TrialInfo_Study3_Motion : TrialInfo
{

    // Factors
    public int temperature;
    public int direction;

    public TrialInfo_Study3_Motion(string rawInfo) : base(rawInfo)
    {
        string[] info = rawInfo.Split(',');
        this.temperature = int.Parse(info[1]);
        this.duration = float.Parse(info[2]);
        this.direction = int.Parse(info[3]);
    }

    public override string GetPiMessage()
    {
        return JsonUtility.ToJson(new PiMessage_Study3_Motion(this));
    }
}

public class PiMessage_Study3_Motion
{
    public string illusion;
    public double thermalVoltage;
    public float duration;
    public int direction;

    public PiMessage_Study3_Motion(TrialInfo_Study3_Motion trialInfo)
    {
        illusion = "motion";
        thermalVoltage = Math.Round(ThermalVoltageMapping.mapping[trialInfo.temperature], 1);
        duration = trialInfo.duration;
        direction = trialInfo.direction;
    }
}