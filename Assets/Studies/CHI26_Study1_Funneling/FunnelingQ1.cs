using UnityEngine;
using UnityEngine.UI;

public class FunnelingQ1 : MonoBehaviour
{

    public Slider slider;
    public Slider q3Slider;
    public GameObject icon;
    public ToolController toolController;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        ResetQuestion();
    }

    // Update is called once per frame
    void Update()
    {

    }

    void OnEnable()
    {
        ResetQuestion();
    }

    public void DisableIcon()
    {
        icon.SetActive(false);
    }

    public void MatchSliders()
    {
        q3Slider.interactable = true;
        q3Slider.value = slider.value;
        q3Slider.interactable = false;
    }

    public void RecordResponse()
    {
        toolController.RecordTrialResponse(slider.value.ToString());
        toolController.NextQuestion();
        MatchSliders();
    }

    public void ResetQuestion()
    {
        slider.value = 0.5f;
    }
}
