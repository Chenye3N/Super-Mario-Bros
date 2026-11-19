using UnityEngine;
using UnityEngine.InputSystem;

[RequireComponent(typeof(Rigidbody2D),typeof(BoxCollider2D))]
public class PlayerController:MonoBehaviour{
    public float moveSpeed=5f;

    private Rigidbody2D rb;
    private Vector2 moveInput;
    public void Move(InputAction.CallbackContext context){
        moveInput=context.ReadValue<Vector2>();
    }

    private void Awake(){
        rb=GetComponent<Rigidbody2D>();
    }

    private void FixedUpdate(){
        rb.linearVelocity=new Vector2(moveInput.x*moveSpeed,rb.linearVelocity.y);
    }
}
