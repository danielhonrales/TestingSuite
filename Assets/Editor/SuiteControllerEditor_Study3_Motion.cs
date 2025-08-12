using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(SuiteController_Study3_Motion))]
public class SuiteControllerEditor_Study3_Motion : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();
        
        SuiteController_Study3_Motion suiteController = (SuiteController_Study3_Motion)target;

        GUILayout.Space(20);

        if (GUILayout.Button("Change Trial Number"))
        {
            suiteController.ChangeTrialNumber();
            suiteController.DisplayTrialInfo(suiteController.trialSet[suiteController.trialNumber]);
        }

        if (GUILayout.Button("Change Participant Number"))
        {
            suiteController.ChangeParticipantNumber();
        }
    }
}
