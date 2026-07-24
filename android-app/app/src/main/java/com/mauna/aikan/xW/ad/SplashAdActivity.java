package com.mauna.aikan.xW.ad;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.FrameLayout;
import android.widget.TextView;
import android.graphics.Color;
import android.view.Gravity;

/**
 * 开屏广告 Activity
 * App启动时展示3-5秒后自动跳转到游戏主界面
 */
public class SplashAdActivity extends Activity {
    private static final String TAG = "SplashAdActivity";
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        FrameLayout container = new FrameLayout(this);
        container.setLayoutParams(new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
        ));
        container.setBackgroundColor(0xFFFF6600); // 橙色背景
        
        // 显示游戏LOGO文字
        TextView title = new TextView(this);
        title.setText("🍎 水果消消乐");
        title.setTextColor(Color.WHITE);
        title.setTextSize(36);
        title.setGravity(Gravity.CENTER);
        
        FrameLayout.LayoutParams params = new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.WRAP_CONTENT,
                FrameLayout.LayoutParams.WRAP_CONTENT
        );
        params.gravity = Gravity.CENTER;
        title.setLayoutParams(params);
        container.addView(title);
        
        // 广告加载提示
        TextView adTip = new TextView(this);
        adTip.setText("广告加载中...");
        adTip.setTextColor(Color.parseColor("#AAFFFFFF"));
        adTip.setTextSize(14);
        
        FrameLayout.LayoutParams tipParams = new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.WRAP_CONTENT,
                FrameLayout.LayoutParams.WRAP_CONTENT
        );
        tipParams.gravity = Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL;
        tipParams.bottomMargin = 200;
        adTip.setLayoutParams(tipParams);
        container.addView(adTip);
        
        setContentView(container);
        
        Log.d(TAG, "📢 开屏广告页面已启动");
        
        // 尝试加载开屏广告
        try {
            Class<?> byManager = Class.forName("com.beizi.sdk.ByManager");
            Class<?> configBuilder = Class.forName("com.beizi.sdk.BySplashConfig$Builder");
            
            Object builder = configBuilder.newInstance();
            builder.getClass().getMethod("codeId", String.class)
                    .invoke(builder, "2078746821353562169");
            builder.getClass().getMethod("container", Object.class)
                    .invoke(builder, container);
            Object config = builder.getClass().getMethod("build").invoke(builder);
            
            byManager.getMethod("loadSplash", Object.class, Activity.class)
                    .invoke(null, config, this);
            
            Log.d(TAG, "📢 开屏广告已加载");
        } catch (Exception e) {
            Log.e(TAG, "❌ 开屏广告加载失败: " + e.getMessage());
        }
        
        // 3.5秒后自动跳转到游戏主页
        new android.os.Handler().postDelayed(() -> {
            try {
                Class<?> mainActivity = Class.forName("com.mauna.aikan.xW.GameMainActivity");
                Intent intent = new Intent(SplashAdActivity.this, mainActivity);
                startActivity(intent);
                finish();
            } catch (Exception e) {
                Log.e(TAG, "跳转失败: " + e.getMessage());
                finish();
            }
        }, 3500);
    }
}
