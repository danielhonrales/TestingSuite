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

    private Vector2Int? lastDrawPos = null;

    void Start()
    {
        rectTransform = drawingSurface.GetComponent<RectTransform>();
        int width = (int)rectTransform.rect.width;
        int height = (int)rectTransform.rect.height;

        texture = new Texture2D(width, height, TextureFormat.RGBA32, false);
        texture.filterMode = FilterMode.Point;

        ClearBoard();

        drawingSurface.texture = texture;
    }

    void Update()
    {
        if (Input.GetMouseButton(0))
        {
            Vector2 localPoint;
            RectTransformUtility.ScreenPointToLocalPointInRectangle(rectTransform, Input.mousePosition, null, out localPoint);

            Vector2Int texCoord = new Vector2Int(
                (int)(localPoint.x + rectTransform.rect.width / 2),
                (int)(localPoint.y + rectTransform.rect.height / 2)
            );

            if (lastDrawPos == null)
            {
                // First point
                DrawAt(texCoord.x, texCoord.y);
                lastDrawPos = texCoord;
            }
            else
            {
                // Draw line between last point and current point
                DrawLine(lastDrawPos.Value, texCoord);
                lastDrawPos = texCoord;
            }
        }
        else
        {
            lastDrawPos = null;  // Reset when not drawing
        }
    }

    public void ClearBoard()
    {
        Color[] clearColorArray = new Color[texture.width * texture.height];
        for (int i = 0; i < clearColorArray.Length; ++i)
            clearColorArray[i] = new Color(0, 0, 0, 0); // fully transparent
        texture.SetPixels(clearColorArray);
        texture.Apply();
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
    }

    void DrawLine(Vector2Int start, Vector2Int end)
    {
        int dx = Mathf.Abs(end.x - start.x);
        int dy = Mathf.Abs(end.y - start.y);

        int sx = start.x < end.x ? 1 : -1;
        int sy = start.y < end.y ? 1 : -1;

        int err = dx - dy;
        int x = start.x;
        int y = start.y;

        while (true)
        {
            DrawAt(x, y);

            if (x == end.x && y == end.y) break;

            int e2 = 2 * err;
            if (e2 > -dy)
            {
                err -= dy;
                x += sx;
            }
            if (e2 < dx)
            {
                err += dx;
                y += sy;
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

        ClearBoard();
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