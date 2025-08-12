using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(SuiteController_Study2_Saltation))]
public class SuiteControllerEditor_Study2_Saltation : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();
        
        SuiteController_Study2_Saltation suiteController = (SuiteController_Study2_Saltation)target;

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
