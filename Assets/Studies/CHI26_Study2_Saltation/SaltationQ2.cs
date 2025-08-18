using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class SaltationQ2 : MonoBehaviour
{

    public List<string> locations;
    public Slider slider;
    public Transform sliderContainer;
    public GameObject sliderPrefab;
    public GameObject icon;
    public TMP_Text countText;
    public ToolController toolController;


    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        locations = new();
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

    public void RecordLocation()
    {
        locations.Add(slider.value.ToString());

        CreateQ3Slider();
        countText.text = "You have marked " + locations.Count.ToString() + " sensations.";

        slider.value = 0;
    }

    public void RecordResponse()
    {
        toolController.RecordTrialResponse(locations.Count.ToString());
        foreach (string val in locations)
        {
            toolController.RecordTrialResponse(val);
        }
        toolController.NextQuestion();
    }

    public void CreateQ3Slider()
    {
        GameObject newSlider = Instantiate(sliderPrefab, sliderContainer);
        newSlider.GetComponent<Slider>().interactable = true;
        newSlider.GetComponent<Slider>().value = slider.value;
        newSlider.GetComponent<Slider>().interactable = false;
    }


    public void ResetQuestion()
    {
        locations = new();
        foreach (Transform child in sliderContainer)
        {
            Destroy(child.gameObject);
        }
        countText.text = "You have marked " + locations.Count.ToString() + " sensations.";
    }
}
