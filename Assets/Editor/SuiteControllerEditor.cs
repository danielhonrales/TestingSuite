using UnityEngine;
using UnityEditor;

[CustomEditor(typeof(SuiteController))]
public class SuiteControllerEditor : Editor
{
    public override void OnInspectorGUI()
    {
        DrawDefaultInspector();
        
        SuiteController suiteController = (SuiteController)target;

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
