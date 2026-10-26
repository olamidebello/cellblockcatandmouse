package world.africandroid.cellblock;
import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.net.http.SslError;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.*;
import android.widget.*;
public class MainActivity extends Activity {
 private static final String HOST="cellblockcatandmouse.africandroid.world", HOME="https://"+HOST+"/";
 private WebView web; private LinearLayout root; private View custom; private WebChromeClient.CustomViewCallback callback;
 @Override public void onCreate(Bundle b){super.onCreate(b);getWindow().setStatusBarColor(0xff10171e);getWindow().setNavigationBarColor(0xff10171e);root=new LinearLayout(this);root.setOrientation(1);root.setBackgroundColor(0xff10171e);setContentView(root);LinearLayout bar=new LinearLayout(this);Button home=new Button(this);home.setText("Home");Button reload=new Button(this);reload.setText("Reload");Button browser=new Button(this);browser.setText("Open browser");bar.addView(home);bar.addView(reload);bar.addView(browser);root.addView(bar);web=new WebView(this);root.addView(web,new LinearLayout.LayoutParams(-1,0,1));WebSettings st=web.getSettings();st.setJavaScriptEnabled(true);st.setDomStorageEnabled(true);st.setAllowFileAccess(false);st.setAllowContentAccess(false);st.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);st.setMediaPlaybackRequiresUserGesture(true);st.setSafeBrowsingEnabled(true);CookieManager.getInstance().setAcceptThirdPartyCookies(web,false);web.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView v,WebResourceRequest request){Uri u=request.getUrl();if("https".equals(u.getScheme())&&HOST.equals(u.getHost())&&(u.getPort()==-1||u.getPort()==443))return false;if("https".equals(u.getScheme())){try{startActivity(new Intent(Intent.ACTION_VIEW,u));}catch(Exception ignored){}}return true;}@Override public void onReceivedSslError(WebView v,SslErrorHandler h,SslError e){h.cancel();error("The game certificate could not be verified. Update the server certificate, then reload.");}@Override public void onReceivedError(WebView v,WebResourceRequest r,WebResourceError e){if(r.isForMainFrame())error("The online game is unavailable. Check your connection and tap Reload.");}});web.setWebChromeClient(new WebChromeClient(){@Override public void onShowCustomView(View v,CustomViewCallback c){if(custom!=null){c.onCustomViewHidden();return;}custom=v;callback=c;root.setVisibility(View.GONE);addContentView(v,new ViewGroup.LayoutParams(-1,-1));v.setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN|View.SYSTEM_UI_FLAG_HIDE_NAVIGATION|View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);}@Override public void onHideCustomView(){closeFullscreen();}});home.setOnClickListener(new View.OnClickListener(){public void onClick(View v){web.loadUrl(HOME);}});reload.setOnClickListener(new View.OnClickListener(){public void onClick(View v){web.loadUrl(HOME);}});browser.setOnClickListener(new View.OnClickListener(){public void onClick(View v){startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(HOME)));}});if(b==null)web.loadUrl(HOME);else web.restoreState(b);}
 private void error(String message){web.loadDataWithBaseURL("https://offline.invalid/","<html><meta name='viewport' content='width=device-width'><body style='background:#10171e;color:white;font:18px sans-serif;padding:28px'><h1>Cellblock Cat &amp; Mouse</h1><p>"+message+"</p></body></html>","text/html","UTF-8",null);}
 private void closeFullscreen(){if(custom!=null){((ViewGroup)custom.getParent()).removeView(custom);custom=null;root.setVisibility(View.VISIBLE);if(callback!=null)callback.onCustomViewHidden();callback=null;}}
 @Override public void onBackPressed(){if(custom!=null)closeFullscreen();else if(web.canGoBack())web.goBack();else super.onBackPressed();}
 @Override protected void onSaveInstanceState(Bundle out){super.onSaveInstanceState(out);web.saveState(out);}
 @Override protected void onPause(){super.onPause();web.onPause();}
 @Override protected void onResume(){super.onResume();if(web!=null)web.onResume();}
 @Override protected void onDestroy(){if(web!=null)web.destroy();super.onDestroy();}
}
