using UnityEngine;

public class DraggableObject : MonoBehaviour
{
    private bool isDragging = false;
    private float zOffset;
    private Vector3 initialPosition;
    private Camera mainCam;

    void Start()
    {
        mainCam = Camera.main;
        if (mainCam == null)
        {
            Debug.LogError("No main camera found! Tag a camera as MainCamera.");
        }

        // Ensure there's a collider
        if (GetComponent<Collider>() == null)
        {
            Debug.LogWarning("No collider found on object. Adding BoxCollider.");
            gameObject.AddComponent<BoxCollider>();
        }
    }

    void OnMouseDown()
    {
        isDragging = true;
        initialPosition = transform.position;
        zOffset = mainCam.WorldToScreenPoint(transform.position).z;
        Debug.Log("Mouse down detected on: " + gameObject.name);
    }

    void OnMouseUp()
    {
        isDragging = false;
        Debug.Log("Mouse up - stopped dragging");
    }

    void Update()
    {
        if (isDragging)
        {
            Vector3 mousePos = Input.mousePosition;
            mousePos.z = zOffset;
            Vector3 worldPos = mainCam.ScreenToWorldPoint(mousePos);
            transform.position = new Vector3(worldPos.x, initialPosition.y, initialPosition.z);
            Debug.Log("Dragging: New position = " + transform.position);
        }
    }
}