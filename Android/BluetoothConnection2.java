package com.example.karolinawierbol.multipilot;
import android.Manifest;
import android.app.AlertDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothServerSocket;
import android.bluetooth.BluetoothSocket;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.os.ParcelUuid;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.telephony.TelephonyManager;
import android.util.Log;
import android.widget.Toast;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.UUID;
import java.util.Set;

import static android.support.v4.app.ActivityCompat.startActivityForResult;
import static android.support.v4.content.ContextCompat.getSystemService;


public class BluetoothConnection2 extends MainActivity{

    private static BluetoothConnection2 instance;

    private OutputStream outputStream = null;
    private InputStream inStream = null;

    public static BluetoothConnection2 getInstance() {
        return instance;
    }

    public void init(int whichPos)  {

        instance = this;

        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (bluetoothAdapter != null) {
            if (bluetoothAdapter.isEnabled()) {
                Set<BluetoothDevice> bondedDevices = bluetoothAdapter.getBondedDevices();
                if(bondedDevices.size() > 0) {
                    Object[] devices = (Object []) bondedDevices.toArray();
                    BluetoothDevice device = (BluetoothDevice) devices[whichPos]; //position - w zaleznosci od pozycji w telefonie

                    Log.d("myDevice",device.getAddress()); //powinine byc adres komputera-servera
                    Log.d("myDevice",device.getName());

                    ParcelUuid[] uuids = device.getUuids(); //pobiera uuid wszystkich urzadzen

                    Log.d("myUuid",uuids[whichPos].toString()); //pozycja musi byc taka sama jak w tab device


                    BluetoothSocket sock = null;
                    Method m = null;
                    try {
                        m = device.getClass().getMethod("createRfcommSocket", new Class[]{int.class});
                        sock = (BluetoothSocket) m.invoke(device,3); //urzadzenie i port
                        //sock = device.createRfcommSocketToServiceRecord(uuids[2].getUuid()); //tym sposobem nie chce dzialac dlatego rboei to co wyzej
                        sock.connect();
                        Log.d("myMsg","polaczylo: "+sock.getRemoteDevice().getName());

                        outputStream = sock.getOutputStream();
                        inStream = sock.getInputStream();
                        Log.d("myMsg", "czy to sie robi?");

                    } catch (NoSuchMethodException e) {
                        e.printStackTrace();
                        Log.d("myMsg","no method: " + e.getMessage());

                    } catch (IllegalAccessException e) {
                        e.printStackTrace();
                        Log.d("myMsg","illegal access: " + e.getMessage());

                    } catch (InvocationTargetException e) {
                        e.printStackTrace();
                        Log.d("myMsg","invocation target: " + e.getMessage());
                    } catch (IOException e) {
                        Log.d("myMsg", "failed conn: " + e.getMessage());
                        e.printStackTrace();
                    }

                }


            } else {
                Log.d("myTag", "nie ma polaczenia!.");
            }
        }
    }

    public ArrayList<String> pairedDevices() {

        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        ArrayList<String> pairedDevs = new ArrayList<>(); //potrzebne do wyswiettlenia sparowanych uzadzen

        if (bluetoothAdapter != null && bluetoothAdapter.isEnabled()) {
            Set<BluetoothDevice> bondedDevices = bluetoothAdapter.getBondedDevices();
            for (BluetoothDevice bt : bondedDevices) { //potrzebne do wsywietlenie sparowanych urzadzen
                pairedDevs.add(bt.getName() + "\n" + bt.getAddress());
            }
        }
        return pairedDevs;
    }

    public boolean isEnabled() {
        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (bluetoothAdapter != null && bluetoothAdapter.isEnabled())
            return true;
        return false;
    }

    public void write(String s)  {
        try {
            outputStream.write(s.getBytes());
        } catch (IOException e)
        {
            Log.d("myMsg","error: "+ e.getMessage());
        }
    }

    public String decodeString(String encodedString) {
        try {
            return new String(encodedString.getBytes(), "UTF-8");
        } catch (UnsupportedEncodingException e) {
            Log.e("unsupCODING", "Unsupported coding exception");
        }
        return "";
    }

    public String receiveData() throws IOException{


        byte[] buffer = new byte[256];
        int bytes;

        try {
            bytes = inStream.read(buffer);
            String readMessage = new String(buffer, 0, bytes);
            readMessage = this.decodeString(readMessage);
            Log.i("receive_data", readMessage + "");
            return readMessage;
        } catch (IOException e){
            Log.i("errorRECVINSIDE", "Error receiving inside method");
            return null;
        }

        // Keep looping to listen for received messages
//        while (true) {
//            try {
//                bytes = inStream.read(buffer);            //read bytes from input buffer
//                String readMessage = new String(buffer, 0, bytes);
//                // Send the obtained bytes to the UI Activity via handler
//                Log.i("receive", readMessage + "");
//            } catch (IOException e) {
//                break;
//            }
//        }
    }

    public InputStream getInStream(){
        return this.inStream;
    }

    public OutputStream getOutputStream(){
        return this.outputStream;
    }

    public void run() {

        int BUFF = 1024;
        byte[] buffer = new byte[BUFF];
        int bytes = 0;
        int b = BUFF;

        while (true) {
            try {
                bytes = inStream.read(buffer, bytes, BUFF - bytes);
            } catch (IOException e) {
                e.printStackTrace();
                Log.d("myMsg","eror: "+e.getMessage());
            }
        }
    }

}
