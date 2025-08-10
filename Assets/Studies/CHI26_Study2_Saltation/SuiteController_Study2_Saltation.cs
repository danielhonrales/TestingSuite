using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class SuiteController_Study2_Saltation : MonoBehaviour
{

    [Space(10)]
    [Header("ExperimentInfo")]
    public string studyFolder;
    public int participantNumber;
    public int trialNumber;
    public List<TrialInfo> trialSet;
    public bool autoPlayOnNext;
    private bool startNextTrial;

    [Space(10)]
    [Header("References")]
    public TMP_Text textParticipantNumber;
    public TMP_Text textTrialNumber;
    public GameObject trialInfoContainer;
    public GameObject trialInfoItemPrefab;
    public CommunicationController communicationController;
    public Button playButton;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        trialNumber = 1;
        ChangeTrialNumber();
        playButton.interactable = false;
        startNextTrial = false;
    }

    // Update is called once per frame
    void Update()
    {
        if (startNextTrial)
        {
            startNextTrial = false;
            NextTrial();
        }
    }

    public void LoadTrialSet()
    {
        trialSet = new();

        using var fileStream = File.OpenRead(String.Format("{0}\\trial_info\\p{1}_trial_set.csv", studyFolder, participantNumber));
        var reader = new StreamReader(fileStream);
        string[] data = reader.ReadToEnd().Split('\n');
        //Debug.Log("Data length = " + data.Length.ToString());
        for (int i = 1; i < data.Length - 1; i++)
        {
            trialSet.Add(new TrialInfo(data[i]));
        }
        for (int i = 0; i < trialSet.Count; i++)
        {
            Debug.Log("Trial " + (i + 1) + " | " + trialSet[i].rawInfo);
        }
        reader.Close();
    }

    public void DisplayTrialInfo(TrialInfo trialInfo)
    {
        Type type = trialInfo.GetType();
        FieldInfo[] fields = type.GetFields();
        for (int i = 0; i < fields.Length; i++)
        {
            // Position
            GameObject trialInfoItem = Instantiate(trialInfoItemPrefab, trialInfoContainer.transform);
            RectTransform rt = trialInfoItem.GetComponent<RectTransform>();
            rt.anchoredPosition = new Vector2(rt.anchoredPosition.x, -rt.rect.height * i);

            // Fill text
            trialInfoItem.transform.Find("Name").GetComponent<TMP_Text>().text = fields[i].Name;
            trialInfoItem.transform.Find("Value").GetComponent<TMP_Text>().text = fields[i].GetValue(trialInfo).ToString();
        }
    }

    public void StartTrialSet()
    {
        LoadTrialSet();
        DisplayTrialInfo(trialSet[0]);
        playButton.interactable = true;
    }

    public void EndTrialSet()
    {
        Debug.Log("");
        Debug.Log("### Completed trial set! ###");
        Debug.Log("");
        playButton.interactable = false;
    }

    public void PlayTrial()
    {
        StartCoroutine(CooldownPlay());
        TrialInfo currentTrial = trialSet[trialNumber - 1];
        communicationController.SendMessageToPi(currentTrial.GetPiMessage());
        communicationController.SendMessageToResponseTool(GetMessageForTool(
            "trialstart",
            new List<string>() { participantNumber.ToString(), trialNumber.ToString(), ((.75f + 3f + currentTrial.duration) * 1000).ToString() }
        ));
    }

    public void NextTrial()
    {
        trialNumber++;
        ChangeTrialNumber();
        playButton.interactable = true;
        if (trialNumber >= trialSet.Count)
        {
            EndTrialSet();
        }
        else if (autoPlayOnNext)
        {
            PlayTrial();
        }
    }

    public void ChangeTrialNumber()
    {
        textTrialNumber.text = trialNumber.ToString();
    }

    public void ChangeParticipantNumber()
    {
        textParticipantNumber.text = "p" + participantNumber.ToString();
        StartTrialSet();
    }

    public void HandleMessageFromTool(string message)
    {
        if (message.StartsWith("nexttrial"))
        {
            startNextTrial = true;
        }
        if (message.StartsWith("response"))
        {
            SaveTrialResponse(message.Split(",")[1..]);
        }
    }

    public void SaveTrialResponse(string[] responseParams)
    {
        string[] responseArray = PadResponseArray(responseParams, 4);
        int responseParticipantNumber = int.Parse(responseArray[0]);
        int responseTrialNumber = int.Parse(responseArray[1]);
        string location = responseArray[2];
        string thermal = responseArray[3];

        string filePath = string.Format("{0}\\trial_responses\\p{1}_response.csv", studyFolder, responseParticipantNumber);
        string directory = Path.GetDirectoryName(filePath);
        if (!Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }
        bool fileExists = File.Exists(filePath);

        using (StreamWriter writer = new(filePath, append: true, Encoding.UTF8))
        {
            if (!fileExists)
            {
                writer.WriteLine("participantNumber,trialNumber,location,thermal");
            }
            writer.WriteLine($"{responseParticipantNumber},{responseTrialNumber},{location},{thermal}");
        }
        Console.WriteLine($"Wrote trial {responseTrialNumber} to CSV.");
    }

    public string[] PadResponseArray(string[] responseParams, int fullLength)
    {
        string[] fullArray = new string[fullLength];
        Array.Copy(responseParams, fullArray, responseParams.Length);
        for (int i = responseParams.Length; i < fullArray.Length; i++)
        {
            fullArray[i] = "";
        }
        return fullArray;
    }

    public string GetMessageForTool(string command, List<string> parameters)
    {
        return string.Format("${0},{1}", command, string.Join(",", parameters));
    }

    public IEnumerator CooldownPlay()
    {
        playButton.interactable = false;
        yield return new WaitForSeconds(5);
        playButton.interactable = true;
    }
}
