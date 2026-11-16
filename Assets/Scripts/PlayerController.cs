using UnityEngine;
using UnityEngine.InputSystem;

public class PlayerController:MonoBehaviour{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    public Rigidbody2D rb;
    private Vector2 horizontalMove;
    public float moveSpeed=5f;
    void Start(){
        rb=GetComponent<Rigidbody2D>();
    }

    // Update is called once per frame
    void Update(){
        rb.linearVelocity=new Vector2(horizontalMove.x*moveSpeed,rb.linearVelocity.y);

    }
    public void Move(InputAction.CallbackContext context){
        horizontalMove=context.ReadValue<Vector2>();
    }
}
