using System.Collections.Generic;

public static class ThermalVoltageMapping
{
    public static readonly Dictionary<int, float> mapping = new()
    {
        {9,     1.5f},
        {6,     1.5f},
        {0,     0},
        {-12,   1.8f},
        {-15,   1.8f}
    };
}