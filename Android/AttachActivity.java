package com.example.karolinawierbol.multipilot;

import android.content.Context;
import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import org.w3c.dom.Text;

import java.io.IOException;

public class AttachActivity extends AppCompatActivity {

    TextView message;
    EditText pass;
    Button buttonProceed;

    final BluetoothConnection2 bc2 = BluetoothConnection2.getInstance();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_attach);

        //GUI elements initialization
        message = (TextView) findViewById(R.id.textView2);
        pass = (EditText) findViewById(R.id.editText);
        buttonProceed = (Button) findViewById((R.id.button3));

        SongsQueue songsQueue = new SongsQueue();

        buttonProceed.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                //get ID
                int given_ID = Integer.parseInt(pass.getText().toString());
                String msg = "ATTACH" + Integer.toString(given_ID) + "\r\n";
                bc2.write(msg);
                Log.i("attachmsg", "przed");
                String server_answer = null;
                try {
                    server_answer = bc2.receiveData();
                    Log.i("attachmsg", server_answer);
                } catch (IOException e) {
                    Log.i("err_recv_msg", "Error while receiving message from server");
                }

                //obsluz odpowiedz
                if (server_answer.equals("ATTACH_ERR\r\n")) {
                    Log.i("attachmsg", "attach_error");
                    Log.i("attachmsg", server_answer);
                    Utils.showToast(AttachActivity.this, "BLAD PRZY DOLACZANIU");
                }
                else if (server_answer.equals("ATTACH_OK\r\n")) {
                    Log.i("attachmsg", "attach ok, proceed");
                    Log.i("attachmsg", server_answer);

                    startActivity(new Intent(AttachActivity.this, QueueUnpriviledgedActivity.class));
                    //startActivity(new Intent(AttachActivity.this, QueueUnpriviledgedActivity.class));
                }
                else {
                    Log.i("attachmsg", "attach_error INNY KOMUNIKAT");
                    Log.i("attachmsg", server_answer);
                    Utils.showToast(AttachActivity.this, "NIEPRAWIDLOWY KOMUNIKAT PROTOKOLU");
                }
                    startActivity(new Intent(AttachActivity.this, QueueUnpriviledgedActivity.class));

            }
        });

    }
}
