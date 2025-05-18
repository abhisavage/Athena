using UnityEngine;

public class LensSimulator : MonoBehaviour
{
    public Transform objectTransform;   // Candle
    public Transform lensTransform;     // Convex lens
    public Transform screenTransform;   // Screen
    public Transform imageTransform;    // Visual image

    public float focalLength = 2f;      // Focal length of convex lens
    public float maxImageDistance = 100f;

    void Update()
    {
        if (!objectTransform || !lensTransform || !screenTransform || !imageTransform)
        {
            Debug.LogWarning("Assign all transforms in Inspector.");
            return;
        }

        // Calculate u (object distance from lens) using physics sign convention
        float u = objectTransform.position.x - lensTransform.position.x;

        // Physics sign convention: object to left of lens => u is negative
        u = -u;

        // If object is at focal point (no image formed)
        if (Mathf.Abs(u - focalLength) < 0.01f)
        {
            imageTransform.gameObject.SetActive(false);
            screenTransform.gameObject.SetActive(false);
            return;
        }

        // Lens formula: 1/f = 1/v - 1/u => v = f*u / (u - f)
        float v = (focalLength * u) / (u - focalLength);

        // Check if image position is too far to display
        if (Mathf.Abs(v) > maxImageDistance)
        {
            imageTransform.gameObject.SetActive(false);
            screenTransform.gameObject.SetActive(false);
            return;
        }

        imageTransform.gameObject.SetActive(true);
        screenTransform.gameObject.SetActive(true);

        // Convert v to Unity world position (relative to lensTransform)
        float imageX = lensTransform.position.x + v;

        // Move screen (only for real images, v > 0)
        screenTransform.gameObject.SetActive(v > 0);
        if (v > 0)
        {
            Vector3 screenPos = screenTransform.position;
            screenPos.x = imageX;
            screenTransform.position = screenPos;
        }

        // Calculate magnification
        float magnification = v / u;

        // Update image position
        Vector3 imgPos = imageTransform.position;
        imgPos.x = imageX;

        float baseY = objectTransform.localScale.y;
        imgPos.y = lensTransform.position.y + baseY * magnification;
        imageTransform.position = imgPos;

        // Update image scale
        float minScale = 0.02f;
        Vector3 imgScale = imageTransform.localScale;
        imgScale.y = Mathf.Max(minScale, Mathf.Abs(magnification)) * (v > 0 ? -1 : 1);

        //imgScale.y = Mathf.Max(minScale, Mathf.Abs(magnification)) * Mathf.Sign(magnification);
        imageTransform.localScale = imgScale;
    }
}
