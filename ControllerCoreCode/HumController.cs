using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HumController : MonoBehaviour
{
    public void HumanTeleport(Vector3 targetPosition, Vector3 targetRotation)
    {
        transform.position = targetPosition;
        transform.rotation = Quaternion.Euler(targetRotation);
    }
}
