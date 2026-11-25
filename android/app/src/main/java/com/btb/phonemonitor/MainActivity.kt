package com.btb.phonemonitor

import android.app.Activity
import android.graphics.BitmapFactory
import android.os.Bundle
import android.view.*
import java.io.*
import java.net.Socket
import java.nio.ByteBuffer
import kotlin.concurrent.thread

class MainActivity : Activity() {
    @Volatile private var out: OutputStream? = null
    // Wi-Fi: change to your PC IP. USB (adb reverse): keep 127.0.0.1
    private val host = "127.0.0.1"; private val port = 5555

    override fun onCreate(s: Bundle?) {
        super.onCreate(s)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or
            View.SYSTEM_UI_FLAG_FULLSCREEN or View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        val sv = SurfaceView(this); setContentView(sv)

        sv.setOnTouchListener { v, e ->
            val act = when (e.actionMasked) {
                MotionEvent.ACTION_DOWN -> 0
                MotionEvent.ACTION_MOVE -> 1
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> 2
                else -> -1 }
            if (act >= 0) {
                val b = ByteBuffer.allocate(9).put(act.toByte())
                    .putFloat((e.x / v.width).coerceIn(0f, 1f))
                    .putFloat((e.y / v.height).coerceIn(0f, 1f)).array()
                thread { try { out?.write(b); out?.flush() } catch (_: Exception) {} }
            }
            true }

        thread {
            while (true) {
                try {
                    val sock = Socket(host, port); sock.tcpNoDelay = true
                    out = sock.getOutputStream()
                    val inp = DataInputStream(BufferedInputStream(sock.getInputStream(), 1 shl 20))
                    while (true) {
                        val n = inp.readInt(); val buf = ByteArray(n); inp.readFully(buf)
                        val bmp = BitmapFactory.decodeByteArray(buf, 0, n) ?: continue
                        val c = sv.holder.lockCanvas() ?: continue
                        c.drawBitmap(bmp, null, android.graphics.Rect(0, 0, c.width, c.height), null)
                        sv.holder.unlockCanvasAndPost(c); bmp.recycle()
                    }
                } catch (_: Exception) { Thread.sleep(1000) }
            }
        }
    }
}
