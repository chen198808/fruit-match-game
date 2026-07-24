# 水果消消乐 - ProGuard混淆规则

# ====== 百益联盟广告SDK（不混淆） ======
-keep class com.anythink.** { *; }
-keep class com.bytedance.** { *; }
-keep class com.qq.e.** { *; }
-keep class com.bun.** { *; }
-keep class com.soyea.** { *; }
-keep class com.by.** { *; }
-keep class by.** { *; }
-dontwarn com.anythink.**
-dontwarn com.bytedance.**
-dontwarn com.qq.e.**
-dontwarn com.bun.**
-dontwarn com.soyea.**
-dontwarn com.by.**
-dontwarn by.**

# ====== 游戏核心类（不混淆） ======
-keep class com.fruitmatch.game.** { *; }
-keep class com.fruitmatch.game.engine.** { *; }
-keep class com.fruitmatch.game.ad.** { *; }
-keep class com.fruitmatch.game.reward.** { *; }
-keep class com.fruitmatch.game.ui.** { *; }

# ====== Gson ======
-keep class com.google.gson.** { *; }
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

# ====== Glide ======
-keep public class * implements com.bumptech.glide.module.GlideModule
-keep public class * extends com.bumptech.glide.module.AppGlideModule
-keep public enum com.bumptech.glide.load.ImageHeaderParser$** {
    **[] $VALUES;
    public *;
}

# ====== Retrofit ======
-keepattributes Signature, InnerClasses, EnclosingMethod
-keepattributes RuntimeVisibleAnnotations, RuntimeVisibleParameterAnnotations
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}
-dontwarn org.codehaus.mojo.animal_sniffer.IgnoreJRERequirement
-dontwarn javax.annotation.**
-dontwarn kotlin.Unit
-dontwarn retrofit2.KotlinExtensions
-dontwarn retrofit2.KotlinExtensions$*

# ====== 通用 ======
-dontwarn org.apache.**
-dontwarn android.support.**
-keep class android.support.** { *; }
-keep interface android.support.** { *; }
