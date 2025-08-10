using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class SaltationQ1 : MonoBehaviour
{

    public GameObject orderNumberPrefab;
    public Transform orderNumberContainer;
    public int currentOrderNumber;
    public List<float> locations;
    public ToolController toolController;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        ResetQ1();
    }

    // Update is called once per frame
    void Update()
    {

    }

    public void CreateOrderNumber(RectTransform buttonRt)
    {
        GameObject orderNumber = Instantiate(orderNumberPrefab, orderNumberContainer);
        RectTransform numberRt = orderNumber.GetComponent<RectTransform>();
        numberRt.anchoredPosition = new Vector2(buttonRt.anchoredPosition.x, buttonRt.anchoredPosition.y - (70 + (40 * (currentOrderNumber - 1))));
        orderNumber.GetComponent<TMP_Text>().text = currentOrderNumber.ToString();
    }

    public void SelectLocation(float location)
    {
        locations.Add(location);
        currentOrderNumber++;
    }

    public void ResetQ1()
    {
        currentOrderNumber = 1;
        for (int i = orderNumberContainer.childCount - 1; i >= 0; i--)
        {
            Destroy(orderNumberContainer.GetChild(i).gameObject);
        }
        locations = new();
    }

    public void SaveResponse()
    {
        toolController.RecordTrialResponse($"[{string.Join(",", locations)}]");
        ResetQ1();
    }
}

