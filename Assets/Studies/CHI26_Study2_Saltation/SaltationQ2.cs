using UnityEngine;

public class SaltationQ2 : MonoBehaviour
{

    public string thermal1;
    public string thermal2;
    public string thermal3;

    public GameObject thermal1UI;
    public GameObject thermal2UI;
    public GameObject thermal3UI;

    public ToolController toolController;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        ResetQ2();
    }

    // Update is called once per frame
    void Update()
    {

    }

    public void SelectThermal1(string thermal)
    {
        thermal1 = thermal;
        thermal1UI.SetActive(false);
        RecordResponse();
    }

    public void SelectThermal2(string thermal)
    {
        thermal2 = thermal;
        thermal2UI.SetActive(false);
        RecordResponse();
    }

    public void SelectThermal3(string thermal)
    {
        thermal3 = thermal;
        thermal3UI.SetActive(false);
        RecordResponse();
    }

    public void RecordResponse()
    {
        if (!thermal1UI.activeSelf && !thermal2UI.activeSelf && !thermal3UI.activeSelf)
        {
            toolController.RecordTrialResponse($"[{thermal1}|{thermal2}|{thermal3}]");
            toolController.NextQuestion();
            ResetQ2();
        }
    }

    public void ResetQ2()
    {
        thermal1 = "";
        thermal2 = "";
        thermal3 = "";
        thermal1UI.SetActive(true);
        thermal2UI.SetActive(true);
        thermal3UI.SetActive(true);
    }
}
