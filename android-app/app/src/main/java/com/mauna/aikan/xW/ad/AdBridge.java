package com.mauna.aikan.xW.ad;

import android.app.Activity;
import android.content.Context;
import android.util.Log;

/**
 * 百益联盟广告桥接类
 * 
 * 作用：桥接 Python (Chaquopy) 和百益联盟 Java SDK
 * Python端通过反射调用这个类的方法
 */
public class AdBridge {
    private static final String TAG = "AdBridge";
    private static boolean initialized = false;
    private static Context appContext;
    
    /**
     * 初始化百益联盟SDK
     */
    public static void init(Context context, String appId) {
        appContext = context.getApplicationContext();
        try {
            // 百益联盟SDK初始化
            Class<?> byManager = Class.forName("com.beizi.sdk.ByManager");
            Class<?> configBuilder = Class.forName("com.beizi.sdk.ByInitConfig$Builder");
            
            Object builder = configBuilder.newInstance();
            builder.getClass().getMethod("appId", String.class).invoke(builder, appId);
            Object config = builder.getClass().getMethod("build").invoke(builder);
            
            byManager.getMethod("init", Context.class, Object.class)
                    .invoke(null, appContext, config);
            
            initialized = true;
            Log.d(TAG, "✅ 百益联盟SDK初始化成功");
        } catch (Exception e) {
            Log.e(TAG, "❌ 百益联盟SDK初始化失败: " + e.getMessage());
        }
    }
    
    /**
     * 加载激励视频
     */
    public static void loadRewardVideo(String codeId) {
        try {
            Class<?> byManager = Class.forName("com.beizi.sdk.ByManager");
            Class<?> configBuilder = Class.forName("com.beizi.sdk.ByRewardVideoConfig$Builder");
            
            Object builder = configBuilder.newInstance();
            builder.getClass().getMethod("codeId", String.class).invoke(builder, codeId);
            Object config = builder.getClass().getMethod("build").invoke(builder);
            
            byManager.getMethod("loadRewardVideo", Object.class, Context.class)
                    .invoke(null, config, appContext);
            
            Log.d(TAG, "📢 激励视频已请求加载");
        } catch (Exception e) {
            Log.e(TAG, "❌ 激励视频加载失败: " + e.getMessage());
        }
    }
    
    /**
     * 播放激励视频
     */
    public static void playRewardVideo(Context context) {
        try {
            Class<?> byManager = Class.forName("com.beizi.sdk.ByManager");
            byManager.getMethod("playRewardVideo", Context.class)
                    .invoke(null, context);
            Log.d(TAG, "📢 激励视频正在播放");
        } catch (Exception e) {
            Log.e(TAG, "❌ 激励视频播放失败: " + e.getMessage());
        }
    }
    
    /**
     * 检查SDK是否已初始化
     */
    public static boolean isInitialized() {
        return initialized;
    }
}
