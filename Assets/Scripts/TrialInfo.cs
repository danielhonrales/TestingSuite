using System;
using System.Collections.Generic;
using UnityEngine;


public class TrialInfo
{
    public string rawInfo;
    public float duration;

    public TrialInfo(string rawInfo)
    {
        this.rawInfo = rawInfo;
        duration = 0;
    }

    public virtual string GetPiMessage()
    {
        return JsonUtility.ToJson(new PiMessage(this));
    }
}

public class PiMessage
{
    public string illusion;

    public PiMessage(TrialInfo trialInfo)
    {
        illusion = "none";
    }
}