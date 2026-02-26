using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using UnityEngine.AI;
using UnityEngine.UI;
using static OVRInput;

public class RobotController : MonoBehaviour
{
    public string robotType;
    public string armLength;
    public string strength;
    public string robotLow;
    public string robotHigh;
    public LayerMask collisionLayer;
    public List<string> comfirmInfo = new List<string> {"null"};
    private NavMeshAgent agent;
    private Vector3 startPosition;
    public bool inputReceived = false;

    public void Teleport(Vector3 targetPosition, Vector3 targetRotation)
    {
        transform.position = targetPosition;
        transform.rotation = Quaternion.Euler(targetRotation);
    }

    public void Pick(string ObjName,string robotName)
    {
        GameObject robot = GameObject.Find(robotName);
        GameObject Obj = GameObject.Find(ObjName);
        Transform ObjMesh = Obj.transform.Find("mesh");
        if (ObjMesh != null)
        {
            Collider meshCollider = ObjMesh.GetComponent<Collider>();
            if (meshCollider != null)
            {
                meshCollider.enabled = false; 
            }
        }
        Rigidbody ObjRb = Obj.GetComponent<Rigidbody>();
        ObjRb.useGravity = false;
        ObjRb.isKinematic = true;

        GameObject hand = robot.transform.Find("Hand")?.gameObject;
        if (hand == null)
        {
            Debug.LogError($"������Hand component not found under robot: {robotName}. Please check the hierarchy.");
            return;
        }

        Obj.transform.position = hand.transform.position;

        Obj.transform.SetParent(hand.transform);

    }

    public void Place(string objName, Vector3 placePosition, Vector3 placeRotation)
    {

        GameObject Obj = GameObject.Find(objName);
        Transform ObjMesh = Obj.transform.Find("mesh");
        if (ObjMesh != null)
        {
            Collider meshCollider = ObjMesh.GetComponent<Collider>();
            if (meshCollider != null)
            {
                meshCollider.enabled = true; 
            }
        }
        Rigidbody ObjRb = Obj.GetComponent<Rigidbody>();
        ObjRb.useGravity = true;
        ObjRb.isKinematic = false;

        GameObject Type = GameObject.Find("StaticObjects");
        Obj.transform.SetParent(Type.transform);
        Obj.transform.position = placePosition;
        Obj.transform.rotation = Quaternion.Euler(placeRotation);
    }

    public string Pull(string ObjName, string robotName, string direction)
    {

        GameObject robot = GameObject.Find(robotName);
        GameObject obj = GameObject.Find(ObjName);

        string pullPointsName = ObjName + "_PullPoints";
        GameObject pullPoints = GameObject.Find(pullPointsName);

        if (obj == null || pullPoints == null)
        {
            return "Object or pull points not found!";
        }

        Transform pullPointsTransform = pullPoints.transform;

        if (pullPointsTransform == null)
        {
            return "Pull points transform not found!";
        }

        Vector3 pulledPosition = obj.transform.position;

        foreach (Transform child in pullPointsTransform)
        {

            if (direction == "(0,0,1)" && child.position.x == obj.transform.position.x &&
                child.position.y == obj.transform.position.y && child.position.z > obj.transform.position.z)
            {
                pulledPosition = child.position;
                break;
            }
            else if (direction == "(0,0,-1)" && child.position.x == obj.transform.position.x &&
                child.position.y == obj.transform.position.y && child.position.z < obj.transform.position.z)
            {
                pulledPosition = child.position;
                break;
            }
            else if (direction == "(1,0,0)" && child.position.x > obj.transform.position.x &&
                child.position.y == obj.transform.position.y && child.position.z == obj.transform.position.z)
            {
                pulledPosition = child.position;
                break;
            }
            else if (direction == "(-1,0,0)" && child.position.x < obj.transform.position.x &&
                child.position.y == obj.transform.position.y && child.position.z == obj.transform.position.z)
            {
                pulledPosition = child.position;
                break;
            }
        }

        if (obj.transform.position != pulledPosition)
        {
            obj.transform.position = pulledPosition; 
            return "Success";
        }

        return "Wrong Direction";
    }

    bool IsItemVisible(GameObject robot, GameObject Obj)
    {

        RaycastHit hit;
        Vector3 direction = Obj.transform.position - robot.transform.position;
        if (Physics.Raycast(robot.transform.position, direction, out hit))
        {
            if (hit.transform == Obj.transform)
            {
                Debug.Log("IsItemVisible:" +1);
                return true;
            }
        }
        Debug.Log("IsItemVisible:" + 0);
        return true;
    }

    private float activeTime;
    public void CommunicateWithHuman(string robotName, string text, string img, Vector3 mark_position)

    {
        MarkPosition(mark_position);
        Debug.Log($"Robot sends message to human: {text} with image.");
        ShowCommunicationUI(robotName, text, img); 
    }

    private void MarkPosition(Vector3 mark_position)
    {
        Debug.Log("MarkPosition");
        GameObject prefabToInstantiate_1 = Resources.Load<GameObject>("MarkBtn"); 
        GameObject MarkBtnObj = Instantiate(prefabToInstantiate_1); 
        MarkBtnObj.name = "MarkBtn";
        MarkBtnObj.SetActive(true);
        RectTransform rectTransform = MarkBtnObj.GetComponent<RectTransform>();
        rectTransform.position = new Vector3(mark_position.x, rectTransform.position.y, mark_position.z);
    }
    private void ShowCommunicationUI(string robotName, string text, string img)
    {

        GameObject humObject = GameObject.Find("Hum");
        if (humObject == null)
        {
            Debug.LogError("HUM object not found.");
            return;
        }

        Transform communicationUITransform = humObject.transform.Find("CommunicationUI");
        if (communicationUITransform == null)
        {
            Debug.LogError("CommunicationUI object not found.");
            return;
        }
        foreach (Transform child in communicationUITransform)
        {
            if (child.gameObject.name.EndsWith("panel"))
            {
                child.gameObject.SetActive(false);
            }
        }
        string panelName = robotName + "_panel";
        Transform targetPanel = communicationUITransform.Find(panelName);
        if (targetPanel != null)
        {
            targetPanel.gameObject.SetActive(true);
            Transform robotMessageTransform = targetPanel.Find("RobotMessage");
            if (robotMessageTransform != null)
            {
                Text messageText = robotMessageTransform.GetComponent<Text>();
                if (messageText != null)
                {
                    messageText.text = text;
                }
                else
                {
                    Debug.LogError("Text component not found in RobotMessage.");
                }
            }
            else
            {
                Debug.LogError("RobotMessage object not found in " + panelName + ".");
            }

            StartCoroutine(HandleInputAndDelay(targetPanel, panelName));
        }
        else
        {
            Debug.LogError(panelName + " object not found in CommunicationUI.");
        }
    }

    private IEnumerator HandleInputAndDelay(Transform targetPanel,string panelName)
    {
        float elapsedTime = 0f;

        Debug.Log("HandleInputAndDelay");
        while (elapsedTime < 15f)
        {
            if (GetDown(OVRInput.Button.One))
            {
                GameObject hum = GameObject.Find("Hum");
                GameObject CommunicationUI = hum.transform.Find("CommunicationUI").gameObject;
                GameObject gamePauseObject = CommunicationUI.transform.Find("MiniMap_panel").gameObject;
                Debug.Log("MiniMap find");
                comfirmInfo.Add("true");
                inputReceived = true;
                targetPanel.gameObject.SetActive(false);
                gamePauseObject.SetActive(true);
                break;

            }
            else if (GetDown(OVRInput.Button.Two))
            {
                comfirmInfo.Add("false");
                inputReceived = true;
                break;
            }

            elapsedTime += Time.deltaTime;
            yield return null;
        }
        if (!inputReceived)
        {
            comfirmInfo.Add("null"); 
        }
        targetPanel.gameObject.SetActive(false);
    }

    public void Move(Vector2 singleRobotMagnitude, float moveSpeed)
    {

        Vector3 forwardDirection = transform.forward * singleRobotMagnitude.x;
        Vector3 rightDirection = transform.right * singleRobotMagnitude.y;
        Vector3 targetPosition = transform.position + forwardDirection + rightDirection;
        Debug.Log("targetPosition" + targetPosition);
        agent = GetComponent<NavMeshAgent>();
        startPosition = transform.position;

        agent.speed = moveSpeed;

        agent.SetDestination(targetPosition);
    }

    public void Rotate(float rotateAngle)
    {
        Quaternion rotation = Quaternion.Euler(0, rotateAngle, 0);

        transform.rotation = transform.rotation * rotation;;
    }
    public (string, string) GetRobotRgbdBase64(string rgbOrRgbd, string robotName, int width, int height)
    {
        string cameraName = "Camera";
        GameObject robotObject = GameObject.Find(robotName);
        Debug.Log(robotObject);
        if (robotObject != null)
        {
            Transform cameraTransform = robotObject.transform.Find(cameraName);
            Debug.Log(cameraTransform);
            if (cameraTransform != null)
            {
                Camera camera = cameraTransform.GetComponent<Camera>();
                if (camera != null)
                {

                    camera.depthTextureMode = DepthTextureMode.Depth;

                    (string rgbBase64, string depthBase64) = CaptureImages(camera, width, height);
                    if (rgbOrRgbd == "rgb")
                    {
                        return (rgbBase64, null);
                    }
                    else if (rgbOrRgbd == "rgbd")
                    {
                        return (rgbBase64, depthBase64);
                    }
                }
                else
                {
                    Debug.LogError($"Camera component not found on GameObject with name {cameraName}!");
                }
            }
            else
            {
                Debug.LogError($"Camera with name {cameraName} not found on robot {robotName}!");
            }
        }
        else
        {
            Debug.LogError($"Robot with name {robotName} not found!");
        }
        return (null, null);
    }
    private (string rgbBase64, string depthBase64) CaptureImages(Camera camera, int width, int height)
    {

        RenderTexture renderTexture = new RenderTexture(width, height, 24);
        RenderTexture depthRenderTexture = new RenderTexture(width, height, 24, RenderTextureFormat.Depth);

        Texture2D rgbTexture = new Texture2D(width, height, TextureFormat.RGB24, false);
        Texture2D depthTexture = new Texture2D(width, height, TextureFormat.RGB24, false);

        RenderTexture currentRT = RenderTexture.active;
        RenderTexture.active = renderTexture;
        camera.targetTexture = renderTexture;
        camera.Render();

        rgbTexture.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        rgbTexture.Apply();

        camera.targetTexture = depthRenderTexture;
        camera.Render();

        depthTexture.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        depthTexture.Apply();

        RenderTexture.active = currentRT;
        camera.targetTexture = null;

        byte[] rgbBytes = rgbTexture.EncodeToPNG();
        string rgbBase64 = Convert.ToBase64String(rgbBytes);
        byte[] depthBytes = depthTexture.EncodeToPNG();
        string depthBase64 = Convert.ToBase64String(depthBytes);

        RenderTexture.ReleaseTemporary(renderTexture);
        RenderTexture.ReleaseTemporary(depthRenderTexture);

        return (rgbBase64, depthBase64);
    }
}
