using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(SuiteController_Study1_Funneling))]
public class SuiteControllerEditor_Study1_Funneling : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();
        
        SuiteController_Study1_Funneling suiteController = (SuiteController_Study1_Funneling)target;

        GUILayout.Space(20);

        if (GUILayout.Button("Change Trial Number"))
        {
            suiteController.ChangeTrialNumber();
        }

        if (GUILayout.Button("Change Participant Number"))
        {
            suiteController.ChangeParticipantNumber();
        }
    }
}
