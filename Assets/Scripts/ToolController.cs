using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ToolController : MonoBehaviour
{
    public string drawingSavePath;
    public ToolTCP toolTCP;

    public TrialResponse trialResponse;
    public GameObject idleScreen;
    public GameObject midTrialScreen;
    public GameObject nextTrialScreen;
    public List<GameObject> responseScreens;
    public int currentQuestion;

    public int participantNumber;
    public int trialNumber;
    public float waitTime;

    public bool testing = false;
    public bool starting = false;

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        if (testing)
        {
            Test();
        }
        if (starting)
        {
            starting = false;
            StartTrial();
        }
    }

    public void StartTrial()
    {
        Debug.Log(string.Format("Staring trial {0}, waiting for {1}", trialNumber, waitTime / 1000));

        trialResponse = new()
        {
            participantNumber = participantNumber,
            trialNumber = trialNumber
        };

        LoadMidTrialScreen();
        StartCoroutine(LoadResponseScreensHelper(waitTime));
    }

    public IEnumerator LoadResponseScreensHelper(float waitTime)
    {
        yield return new WaitForSeconds(waitTime / 1000f);
        Debug.Log("Trial finished, loading response UI...");
        LoadResponseScreens();
    }

    public void LoadMidTrialScreen()
    {
        idleScreen.SetActive(false);
        midTrialScreen.SetActive(true);
    }

    public void LoadResponseScreens()
    {
        Debug.Log("Loading response screen");
        idleScreen.SetActive(false);
        midTrialScreen.SetActive(false);

        foreach (GameObject responseScreen in responseScreens)
        {
            responseScreen.SetActive(false);
        }

        currentQuestion = 0;
        responseScreens[currentQuestion].SetActive(true);
    }

    public void NextQuestion()
    {
        responseScreens[currentQuestion].SetActive(false);

        if (currentQuestion < responseScreens.Count - 1)
        {
            currentQuestion++;
            responseScreens[currentQuestion].SetActive(true);
        }
        else
        {
            EndTrial();
        }
    }

    public void SkipRestOfTrial()
    {
        responseScreens[currentQuestion].SetActive(false);
        currentQuestion = responseScreens.Count - 1;
        responseScreens[currentQuestion].SetActive(true);
    }

    public void EndTrial()
    {
        foreach (GameObject responseScreen in responseScreens)
        {
            responseScreen.SetActive(false);
        }
        StartCoroutine(EndTrialHelper());
    }

    private IEnumerator EndTrialHelper()
    {
        toolTCP.SendMessageToSuite(string.Format("response," + trialResponse.ToListString()));
        midTrialScreen.SetActive(true);
        yield return new WaitForSeconds(.1f);
        midTrialScreen.SetActive(false);
        nextTrialScreen.SetActive(true);
    }

    public void EndExperiment()
    {
        idleScreen.SetActive(true);
    }

    public void RecordTrialResponse(string response)
    {
        trialResponse.responses.Add(response);
    }

    public void HandleMessageFromSuite(string message)
    {
        if (message.StartsWith("$trialstart"))
        {
            string[] messageParams = message.Split(",");
            participantNumber = int.Parse(messageParams[1]);
            trialNumber = int.Parse(messageParams[2]);
            waitTime = float.Parse(messageParams[3]);

            starting = true;    // Must use bool instead of func because SetActive only possible in main thread
        }

        if (message.StartsWith("$experimentend"))
        {
            EndExperiment();
        }
    }

    public void Test()
    {
        trialNumber = 999;
        waitTime = 3000;
        StartTrial();
        testing = false;
    }

    public void NextTrial()
    {
        nextTrialScreen.SetActive(false);
        idleScreen.SetActive(true);
        string message = "nexttrial";
        toolTCP.SendMessageToSuite(message);
    }

    public class TrialResponse
    {
        public int participantNumber;
        public int trialNumber;
        public List<string> responses = new();

        public string ToListString()
        {
            return string.Format("{0},{1},{2}",
                participantNumber,
                trialNumber,
                string.Join(",", responses)
            );
        }
    }
}
