using System.Collections.Generic;

public static class ThermalVoltageMapping
{
    public static readonly Dictionary<int, float> targetTempToVoltMapping = new()
    {
        {42,     1.2f},
        {41,     1.6f},
        {40,     1.35f},
        {39,     1.5f},
        {38,     1.65f},
        {37,     1.3f},
        {36,     1.2f},
        {35,     1.1f},
        
        {34,     0},
        {33,     0},
        {31,     0},
        {30,     0},
        {29,     0},
        { 0,     0},
        
        { 22,   -0.5f + coldBoost},
        {21,   -0.6f + coldBoost},
        {20,   -0.7f + coldBoost},
        {19,   -0.9f + coldBoost},
        {18,   -1.1f + coldBoost},
        {17,   -1.3f + coldBoost},
        {16,   -1.5f + coldBoost},
        {15,   -1.7f + coldBoost},
        {14,   -1.7f + coldBoost},
        { 12,   -2.3f + coldBoost},
    };
    private static readonly float coldBoost = .5f;
}