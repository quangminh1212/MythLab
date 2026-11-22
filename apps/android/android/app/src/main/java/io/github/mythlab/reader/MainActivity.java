package io.github.mythlab.reader;

import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.view.Window;

import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsControllerCompat;

import com.getcapacitor.BridgeActivity;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(MediaPlaybackPlugin.class);
        registerPlugin(ThemeBarsPlugin.class);
        super.onCreate(savedInstanceState);
    }

    /**
     * Paints the status and navigation bars to the web theme.
     * Capacitor SystemBars only flips icon contrast and then resets the decor background to the
     * teal window theme, so the bars never followed the page. Target SDK 36 is edge-to-edge: the
     * inset padding shows the decor background, which is why that colour is set too.
     */
    @CapacitorPlugin(name = "ThemeBars")
    public static class ThemeBarsPlugin extends Plugin {
        @PluginMethod
        public void apply(PluginCall call) {
            String color = call.getString("color", "#0D9488");
            boolean dark = Boolean.TRUE.equals(call.getBoolean("dark", false));
            final int parsed;
            try {
                parsed = Color.parseColor(color);
            } catch (IllegalArgumentException e) {
                call.reject("bad color");
                return;
            }
            getBridge().executeOnMainThread(() -> {
                if (getActivity() == null) {
                    call.resolve();
                    return;
                }
                Window w = getActivity().getWindow();
                w.setStatusBarColor(parsed);
                w.setNavigationBarColor(parsed);
                if (Build.VERSION.SDK_INT >= 28) w.setNavigationBarDividerColor(parsed);
                w.getDecorView().setBackgroundColor(parsed);
                WindowInsetsControllerCompat ctl = WindowCompat.getInsetsController(w, w.getDecorView());
                // dark page → light icons
                ctl.setAppearanceLightStatusBars(!dark);
                ctl.setAppearanceLightNavigationBars(!dark);
                call.resolve();
            });
        }
    }
}
