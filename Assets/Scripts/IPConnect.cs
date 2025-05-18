using UnityEngine;
using TMPro;

public class IPConnect : MonoBehaviour
{
    public TMP_InputField ipInput;
    public TMP_InputField portInput;

    public void OpenBrowser()
    {
        string ip = ipInput.text.Trim();
        string port = portInput.text.Trim();

        if (string.IsNullOrEmpty(ip) || string.IsNullOrEmpty(port))
        {
            Debug.LogWarning("IP or Port is empty!");
            return;
        }

        string url = $"http://{ip}:{port}";
        Application.OpenURL(url);
    }
}
