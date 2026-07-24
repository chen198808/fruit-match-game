package com.mauna.aikan.xW.ad;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.FrameLayout;

/**
 * 激励视频广告 Activity
 * 全屏播放激励视频广告
 */
public class RewardVideoActivity extends Activity {
    private static final String TAG = "RewardVideoActivity";
    private static RewardVideoCallback sCallback;
    
    public interface RewardVideoCallback {
        void onReward();
        void onClose();
        void onError(String msg);
    }
    
    public static void setCallback(RewardVideoCallback callback) {
        sCallback = callback;
    }
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 创建一个全屏容器
        FrameLayout container = new FrameLayout(this);
        container.setLayoutParams(new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT
        ));
        container.setBackgroundColor(0xFF000000);
        setContentView(container);
        
        Log.d(TAG, "🎬 激励视频广告页面已启动");
        
        // 通过AdBridge播放广告
        AdBridge.playRewardVideo(this);
        
        // 3秒后模拟关闭（实际应该等广告播放完成回调）
        // 这里简单的延迟处理，实际项目中应该监听SDK回调
        new android.os.Handler().postDelayed(() -> {
            if (sCallback != null) {
                sCallback.onReward();
            }
            finish();
        }, 5000);
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (sCallback != null) {
            sCallback.onClose();
        }
    }
}
