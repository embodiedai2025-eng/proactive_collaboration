using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Door : MonoBehaviour
{
    
    
    [Header("��ת�Ƕ�")]
    public float angle = 90f;
    [Header("����")]
    public bool reversal = false;
    [Header("��ת�ٶ�")]
    public float openSpeed = 100;
    [Header("��ת����")]
    public bool xAxial =false, yAxial=true, zAxial=false;


    private float menAngle = 0;

    

    private bool state = false;

    
    
    
    [HideInInspector]
    public bool ActivateControl = true;
    Vector3 angleStart = Vector3.zero;
    Vector3 angleEnd = Vector3.zero;
    private bool open = false;
    protected void Start()
    {
        angleStart = transform.eulerAngles;
        Vector3 vector = Vector3.zero;
        if (xAxial)
            vector.x = angle;
        if (yAxial)
            vector.y = angle;
        if (zAxial)
            vector.z = angle;
        angleEnd = transform.eulerAngles + vector;

        if (transform.GetComponent<Rigidbody>() == null)
        {
            transform.gameObject.AddComponent<Rigidbody>().isKinematic = true;
            transform.GetComponent<Rigidbody>().useGravity = false;
        }
        else
        {
            transform.GetComponent<Rigidbody>().useGravity = false;
            transform.GetComponent<Rigidbody>().isKinematic = true;
        }
    }
    public bool test = false;
    private void Update()
    {
        
        if (test==true)
        {
            Debug.Log("test" + test);
            DoorRotate();
        }
    }
    void OnCollisionEnter(Collision collision)
    {
        GameObject[] l = GameObject.FindGameObjectsWithTag("hand");
        
        for (int i = 0; i < l.Length; i++)
        {
            Transform[] t = l[i].GetComponentsInChildren<Transform>();

            for (int j = 0; j < t.Length; j++)
            {
                if (collision.transform == t[j])
                {
                    Debug.Log("collision.transform == t[j]" + t[j].name);
                    test = true;
                }
            }
        }
        Debug.Log("Door OnCollisionEnter" + transform.name);
        Debug.Log("Door OnCollisionEnter collision" + collision.transform.gameObject);
        
    }

    private void OnTriggerEnter(Collider other)
    {
        Debug.Log("Door OnTriggerEnter" + transform.name);
        Debug.Log("Door OnTriggerEnter Collider other" + other.transform.gameObject);

        GameObject[] l = GameObject.FindGameObjectsWithTag("hand");
        
        for (int i = 0; i < l.Length; i++)
        {
            Transform[] t = l[i].GetComponentsInChildren<Transform>();

            for (int j = 0; j < t.Length; j++)
            {
                if (other.transform == t[j])
                {
                    Debug.Log("collision.transform == t[j]" + t[j].name);
                    test = true;
                }
            }
        }

    }
    private void DoorRotate()
    {
        menAngle += openSpeed * Time.deltaTime;
        Debug.Log("menAngle" + menAngle);
        if (menAngle < angle)
        {
            int i = 1;
            if (reversal)
                i = -1;
            Vector3 vector = Vector3.zero;
            if (xAxial)
                vector.x = openSpeed * Time.deltaTime;
            if (yAxial)
                vector.y = openSpeed * Time.deltaTime;
            if (zAxial)
                vector.z = openSpeed * Time.deltaTime;
            Debug.Log("vector"+vector);
            Debug.Log("state"+state);
            if (state == false)
            {
                transform.Rotate(vector * i);
            }
            else
            {
                transform.Rotate(vector * -1 * i);
            }
        }
        else
        {
            Debug.Log("state" + state);
            menAngle = 0;
            if (state)
            {
                state = false;
            }
            else
            {
                state = true;
            }
            test = false;
        }
    }

}
