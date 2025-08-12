using UnityEngine;

public class SlideIcon : MonoBehaviour
{

    public RectTransform rt;
    public Vector2 pos1;
    public Vector2 pos2;
    public float duration = 2f;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        rt = GetComponent<RectTransform>();
        StartCoroutine(SlideBackAndForth());
    }

    // Update is called once per frame
    void Update()
    {

    }

    private System.Collections.IEnumerator SlideBackAndForth()
    {
        while (true)
        {
            yield return Slide(rt, pos1, pos2, duration);
            yield return Slide(rt, pos2, pos1, duration);
        }
    }

    private System.Collections.IEnumerator Slide(RectTransform rect, Vector2 from, Vector2 to, float time)
    {
        float elapsed = 0f;
        while (elapsed < time)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / time;

            // Ease in and out using SmoothStep
            t = Mathf.SmoothStep(0f, 1f, t);

            rect.anchoredPosition = Vector2.Lerp(from, to, t);
            yield return null;
        }
        rect.anchoredPosition = to; // Ensure exact final position
    }
}
