using UnityEngine;
using UnityEngine.UI;
using System.IO;

public class DrawingBoard : MonoBehaviour
{
    public RawImage drawingSurface;
    public Color drawColor = Color.red;
    public int brushSize = 5;

    private Texture2D texture;
    private RectTransform rectTransform;
    public ToolController toolController;

    void Start()
    {
        rectTransform = drawingSurface.GetComponent<RectTransform>();
        int width = (int)rectTransform.rect.width;
        int height = (int)rectTransform.rect.height;

        texture = new Texture2D(width, height, TextureFormat.RGBA32, false);
        texture.filterMode = FilterMode.Point;

        Color[] clearColorArray = new Color[texture.width * texture.height];
        for (int i = 0; i < clearColorArray.Length; ++i)
            clearColorArray[i] = new Color(0, 0, 0, 0); // fully transparent

        texture.SetPixels(clearColorArray);
        texture.Apply();

        drawingSurface.texture = texture;
    }

    void Update()
    {
        // Handle touch (mobile) or mouse (editor testing)
        if (Input.GetMouseButton(0))
        {
            Vector2 localPoint;
            RectTransformUtility.ScreenPointToLocalPointInRectangle(rectTransform, Input.mousePosition, null, out localPoint);

            Vector2Int texCoord = new Vector2Int(
                (int)(localPoint.x + rectTransform.rect.width / 2),
                (int)(localPoint.y + rectTransform.rect.height / 2)
            );

            DrawAt(texCoord.x, texCoord.y);
        }
    }

    void DrawAt(int x, int y)
    {
        for (int i = -brushSize; i <= brushSize; i++)
        {
            for (int j = -brushSize; j <= brushSize; j++)
            {
                int px = x + i;
                int py = y + j;
                if (px >= 0 && px < texture.width && py >= 0 && py < texture.height)
                {
                    texture.SetPixel(px, py, drawColor);
                }
            }
        }
        texture.Apply();
    }

    public void SaveDrawing()
    {
        byte[] bytes = texture.EncodeToPNG();
        string folderPath = Path.Combine(toolController.drawingSavePath, "p" + toolController.participantNumber.ToString());
        string path = Path.Combine(folderPath, string.Format("p{0}_trial{1}_drawing.png", toolController.participantNumber, toolController.trialNumber));
        if (!Directory.Exists(folderPath))
        {
            Directory.CreateDirectory(folderPath);
        }
        File.WriteAllBytes(path, bytes);
        Debug.Log("Saved drawing to: " + path);
    }

    public void ClearDrawing()
    {
        // Fill the texture with fully transparent pixels
        Color[] clearColors = new Color[texture.width * texture.height];
        for (int i = 0; i < clearColors.Length; i++)
        {
            clearColors[i] = new Color(0, 0, 0, 0);  // transparent
        }

        texture.SetPixels(clearColors);
        texture.Apply();
    }
}