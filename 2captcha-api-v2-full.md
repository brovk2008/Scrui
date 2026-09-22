<div class="intro">

<img src="/assets/captcha-api-docs/img/alibaba-captcha.svg" width="320" height="160" alt="alibaba" />

<h1>Alibaba captcha</h1>

</div>

A token-based method for bypassing Alibaba captcha.

> **IMPORTANT**: Some parameters are generated dynamically and might differ with every page load protected by Alibaba captcha.

## Task Types

- **AlibabaTaskProxyless**: We use our own proxy pool to solve the captchas.
- **AlibabaTask**: We use the proxy you provide.

## How to Find All Required Parameters

To get the parameters needed to create a task, you need to analyze the network traffic of the page and the data returned by the server when the captcha appears.

### Step 1. Getting the Page with the Captcha

1. Open the website and perform the action that triggers the captcha (like a login attempt).
2. Open **DevTools → Network**.
3. Find the request after which the server returns an HTML captcha page instead of a regular JSON response.

The page response usually contains an object like this:

```javascript
var requestInfo = {
  data,
  region,
  sceneId,
  token,
  traceid,
  type,
  userId,
  userUserId
}
```

### Step 2. Extracting Parameters from requestInfo

You need to extract the following values from the `requestInfo` object:

| Task Parameter | Source          |
| --------------- | ----------------- |
| sceneId         | `sceneId` field    |
| userId          | `userId` field     |
| userUserId      | `userUserId` field |
| verifyType      | `type` field       |
| region          | `region` field     |
| UserCertifyId   | `traceid` field    |

You also need to save the following:

| Parameter | Source         |
| -------- | ---------------- |
| u_atoken | `token` value |
| u_asig   | `traceid` value |

These parameters are used when resending the request after successfully solving the captcha.

### Step 3. Finding sceneId via Network Requests

If the `requestInfo` object is missing or obfuscated, you can find the `sceneId` value another way:

1. Go to the **Network** tab.
2. Search for the following keys:

   * `sceneId`
   * `CaptchaSceneId`
   * `sId`

3. Check the contents of requests and responses related to captcha verification or initialization.

### Step 4. Getting the prefix

The `prefix` parameter is usually found in requests related to loading the captcha task.

To find it:

1. Find the requests made during captcha initialization.
2. Open the request URL.
3. Look for the `prefix` parameter in the query string, URL parameters, or the server response body.

### Step 5. Getting apiGetLib

The `apiGetLib` parameter is a link to the captcha JavaScript library.

You can usually get it in one of the following ways:

* Find the `<script>` tag on the captcha page that loads the library.
* Find the request to the `AliyunCaptcha.js` file in the **Network** tab.
* Build the URL using the template the website uses.

Example:

```text
https://o.example.com/captcha-frontend/aliyunCaptcha/AliyunCaptcha.js?t=2041
```

### Final Set of Parameters

As a result, you should get the following values:

```json
{
  "sceneId": "...",
  "prefix": "...",
  "userId": "...",
  "userUserId": "...",
  "verifyType": "...",
  "region": "...",
  "UserCertifyId": "...",
  "apiGetLib": "..."
}
```

You also need to save:

```json
{
  "u_atoken": "...",
  "u_asig": "..."
}
```

These values are used to re-execute the request after getting the captcha solution.

## Specification for AlibabaTaskProxyless Task Type

| Property | Type | Required | Description |
| -------- | --- | ---------- | -------- |
| **type** | *String* | **Yes** | Task type: <br>**AlibabaTaskProxyless** <br> **AlibabaTask** |
| **websiteURL** | *String* | **Yes** | Full URL of the target web page where the captcha is loaded |
| **sceneId** | *String* | **Yes** | Captcha scenario identifier, passed in this format: `"sceneId":"1ww7426c4"` |
| **prefix** | *String* | **Yes** | Captcha initialization parameter passed in the URL of the request used to load the task text on the page. For example, if the URL looks like https://dlw3kug.captcha-open.example.aliyuncs.com/, the `prefix` value matches the subdomain, which is `dlw3kug` |
| userId | *String* | No | Unique identifier of the user or session on the website side |
| userUserId | *String* | No | Additional (secondary) user identifier |
| verifyType | *String* | No | Version or type of the captcha verification mechanism |
| region | *String* | No | Region of the server or data center processing the captcha |
| userCertifyId | *String* | No | Unique verification ID linked to the current captcha session |
| apiGetLib | *String* | No | Link to the captcha JS library used by the site. The value is formed on the client side and might be generated dynamically on every page render |
| userAgent | *String* | No | Browser User-Agent used to open the page |

## Specification for AlibabaTask Task Type

| Property | Type | Required | Description |
| -------- | --- | ---------- | -------- |
| **proxyType** | *String* | **Yes** | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String* | **Yes** | IP address or hostname of the proxy server |
| **proxyPort** | *Number* | **Yes** | Proxy server port |
| proxyLogin | *String* | No | Login for proxy server authentication |
| proxyPassword | *String* | No | Password for proxy server authentication |

## Request Examples

Method: [createTask](/api-docs/create-task)

API Endpoint: `https://api.2captcha.com/createTask`

### AlibabaTaskProxyless Request Example

```json
{
   "clientKey":"YOUR_API_KEY",
   "task":{
      "type":"AlibabaTaskProxyless",
      "websiteUrl":"https://www.example.com",
      "sceneId":"abc123xyz4",
      "prefix":"def456gh",
      "userId":"Abc123Def456Ghi789Jkl012Mno345Pqr678Stu901=",
      "userUserId":"Xyz987Abc654Def321Ghi098Jkl765Mno432Pqr109=",
      "verifyType":"1.0",
      "region":"sgp",
      "UserCertifyId":"abc123def456ghi789jkl012mno345pq",
      "apiGetLib":"https://o.example.com/captcha-frontend/aliyunCaptcha/AliyunCaptcha.js?t=1234",
      "userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
   }
}
```

### AlibabaTask Request Example with Proxy

```json
{
   "clientKey":"YOUR_API_KEY",
   "task":{
      "type":"AlibabaTask",
      "websiteUrl":"https://www.example.com",
      "sceneId":"abc123xyz4",
      "prefix":"def456gh",
      "userId":"Abc123Def456Ghi789Jkl012Mno345Pqr678Stu901=",
      "userUserId":"Xyz987Abc654Def321Ghi098Jkl765Mno432Pqr109=",
      "verifyType":"1.0",
      "region":"sgp",
      "UserCertifyId":"abc123def456ghi789jkl012mno345pq",
      "apiGetLib":"https://o.example.com/captcha-frontend/aliyunCaptcha/AliyunCaptcha.js?t=1234",
      "userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
      "proxyType":"http",
      "proxyAddress":"1.2.3.4",
      "proxyPort":8080,
      "proxyLogin":"login",
      "proxyPassword":"password"
   }
}
```

## Response Example

Method: [getTaskResult](/api-docs/get-task-result)

API Endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
  "errorId": 0,
  "status": "ready",
  "solution": {
    "data": {
      "tokens": "{\"sceneId\":\"abc123xyz4\",\"certifyId\":\"aBcDeF1234\",\"deviceToken\":\"ABC_WEB#1234...xyz789=\",\"data\":\"AbC123xYz...DeF456qWe789\"}"
    }
  }
}
```

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/altcha-captcha.svg" width="320" height="160" alt="Altcha" />

<h1>Altcha captcha</h1>

</div>

Token-based method for automated solving of `Altcha`.

> Token-based method requires `challengeurl` or `challengeJSON` parameter, as well as proxy (not required).

## Task types
- **AltchaTaskProxyless** - we use our own proxies pool to load and solve the captcha
- **AltchaTask** - we use your proxies

| Property             | Type      | Required | Description                                              |
| -------------------- | --------  | -------- | -------------------------------------------------------- |
| **type**             | *String*  | **Yes**  | Task type: <br>**AltchaTaskProxyless** <br>  **AltchaTask**                     |
| **websiteURL**       | *String*  | **Yes**  | The full URL of target web page where the captcha is loaded. |
| **challengeURL**     | *String*  | **Yes***  | The value of the `src` parameter for the `iframe` element containing the captcha on the page. |
| **challengeJSON**    | *String*  | **Yes***  | The contents of the file from the 'challenge_url' parameter |

> **\*** You can send either `challengeURL` or `challengeJSON` parameter, but not two of it simultaneously.

## AltchaTask type specification

`AltchaTask` extends `AltchaTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |

## Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### AltchaTaskProxyless
```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "AltchaTaskProxyless",
    "websiteURL": "https://site.com/",
    "challengeURL": "https://.../captcha/api/altcha/challenge"
  }
}
```

### AltchaTask

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "AltchaTask",
    "websiteURL": "https://site.com/",
    "challengeURL": "https://.../captcha/api/altcha/challenge",
    "proxyType":"http",
    "proxyAddress":"1.2.3.4",
    "proxyPort": "8080",
    "proxyLogin":"user23",
    "proxyPassword":"p4$w0rd"
  }
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "cost": "0.0012",
    "createTime": 1754563182,
    "endTime": 1754563190,
    "errorId": 0,
    "ip": "46.53.232.76",
    "solution":
    {
        "token":"eyJhbGdvcml0aG0iOiJTSEEtMjU2IiwiY2hhbGxlbmdlIjoiZWFiOTE3NjRkM2Y5ZDBjMGU4ZmR......."
    },
    "solveCount": 1,
    "status": "ready"
}

```
Use the token to interact with the target website.

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/aws.svg" width="320" height="160" alt="Amazon WAF captcha" />

<h1>Amazon WAF Captcha</h1>

</div>

Token-based method for automated solving of Amazon AWS captcha.
We support two methods for solving this type of captcha: with `challenge_script` and with `jsapiScript`

## Task types
- **AmazonTaskProxyless** - we use our own proxies pool to load and solve the captcha
- **AmazonTask** - we use your proxies

### challenge_script option:
### Task specification

| Property        | Type     | Required | Description                                                 |
| --------------- | -------- | -------- | ----------------------------------------------------------- |
| **type**        | *String* | **Yes**  | Task type: <br>**AmazonTaskProxyless** <br>  **AmazonTask** |
| **websiteURL**  | *String* | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **websiteKey**  | *String* | **Yes**  | Value of `key` parameter you found on the page              |
| **iv**          | *String* | **Yes**  | Value of `iv` parameter you found on the                    |
| **context**     | *String* | **Yes**  | Value of `context` parameter you found on the page          |
| challengeScript | *String* | No       | The source URL of `challenge.js` script on the page         |
| captchaScript   | *String* | No       | The source URL of `captcha.js` script on the page           |

> Important: for each request to our API, you need to get a new values `websiteKey` `iv` `context`. The values of `websiteKey` `iv` `context` must be searched in the page code.


### jsapiScript option:
### Task specification

| Property        | Type     | Required | Description                                                 |
| --------------- | -------- | -------- | ----------------------------------------------------------- |
| **type**        | *String* | **Yes**  | Task type: <br>**AmazonTaskProxyless** <br>  **AmazonTask** |
| **websiteURL**  | *String* | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **websiteKey**  | *String* | **Yes**  | Value of `key` parameter you found on the page              |
| **jsapiScript** | *String* | **Yes**  | The source URL of `jsapiScript.js` script on the page       |

## AmazonTask Task type specification

`AmazonTask` extends `AmazonTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
|------------------|-----------|----------|----------------------------------------------------------|
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### AmazonTaskProxyless request example

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "AmazonTaskProxyless",
        "websiteURL": "https://efw47fpad9.execute-api.us-east-1.amazonaws.com/latest",
        "challengeScript": "https://41bcdd4fb3cb.610cd090.us-east-1.token.awswaf.com/41bcdd4fb3cb/0d21de737ccb/cd77baa6c832/challenge.js",
        "captchaScript": "https://41bcdd4fb3cb.610cd090.us-east-1.captcha.awswaf.com/41bcdd4fb3cb/0d21de737ccb/cd77baa6c832/captcha.js",
        "websiteKey": "AQIDA...wZwdADFLWk7XOA==",
        "context": "qoJYgnKsc...aormh/dYYK+Y=",
        "iv": "CgAAXFFFFSAAABVk"
    }
}
```

### AmazonTask request example
#### challenge_script option:
```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"AmazonTask",
        "websiteURL": "https://efw47fpad9.execute-api.us-east-1.amazonaws.com/latest",
        "challengeScript": "https://41bcdd4fb3cb.610cd090.us-east-1.token.awswaf.com/41bcdd4fb3cb/0d21de737ccb/cd77baa6c832/challenge.js",
        "captchaScript": "https://41bcdd4fb3cb.610cd090.us-east-1.captcha.awswaf.com/41bcdd4fb3cb/0d21de737ccb/cd77baa6c832/captcha.js",
        "websiteKey": "AQIDA...wZwdADFLWk7XOA==",
        "context": "qoJYgnKsc...aormh/dYYK+Y=",
        "iv": "CgAAXFFFFSAAABVk",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": "8080",
        "proxyLogin": "user23",
        "proxyPassword": "p4$w0rd"
    }
}
```
#### jsapiScript option:
```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"AmazonTask",
        "websiteURL": "https://efw47fpad9.execute-api.us-east-1.amazonaws.com/latest",
        "jsapiScript":"https://82d925f87a91.edge.captcha-sdk.awswaf.com/82d925f87a91/jsapi.js",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": "8080",
        "proxyLogin": "user23",
        "proxyPassword": "p4$w0rd"
    }
}
```

## Result example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "captcha_voucher": "eyJ0eXAiO...oQjTnJlBvAW4",
        "existing_token": "f8ab5749-f916-...5D8yAA39JtKVbw="
    },
    "cost": "0.00145",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 0
}
```


## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
  // https://github.com/2captcha/2captcha-php

    require(__DIR__ . '/../src/autoloader.php');

    $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

    try {a
        $result = $solver->amazon_waf([
            'sitekey' => 'AQIDAHjcYu/Gj...AMGgGCSqGSIb3DQEHATAeBglg',
            'url'     => 'https://non-existent-example.execute-api.us-east-1.amazonaws.com',
            'iv'      => 'test_iv',
            'context' => 'test_context'
        ]);
    } catch (\Exception $e) {
        die($e->getMessage());
    }

    die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
# https://github.com/2captcha/2captcha-python
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

solver = TwoCaptcha(api_key)

try:
    result = solver.amazon_waf(sitekey='0x1AAAAAAAAkg0s2VIOD34y5',
                            iv='CgAHbCe2GgAAAAAj',
                            context='9BUgmlm48F92WUoqv97a49ZuEJJ50TCk9MVr3C7WMtQ0X6flVbufM4n8mjFLmbLVAPgaQ1Jydeaja94iAS49ljb+sUNLoukWedAQZKrlY4RdbOOzvcFqmD/ZepQFS9N5w15Exr4VwnVq+HIxTsDJwRviElWCdzKDebN/mk8/eX2n7qJi5G3Riq0tdQw9+C4diFZU5E97RSeahejOAAJTDqduqW6uLw9NsjJBkDRBlRjxjn5CaMMo5pYOxYbGrM8Un1JH5DMOLeXbq1xWbC17YSEoM1cRFfTgOoc+VpCe36Ai9Kc='
                            url='https://non-existent-example.execute-api.us-east-1.amazonaws.com/latest')
except Exception as e:
    sys.exit(e)

else:
    sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
  // https://github.com/2captcha/2captcha-csharp
  using System;
  using System.Linq;
  using TwoCaptcha.Captcha;

  namespace TwoCaptcha.Examples
  {
      public class AmazonWafExample
      {
          public void Main()
          {
              TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
              AmazonWaf captcha = new AmazonWaf();
              captcha.SetSiteKey("AQIDAHjcYu/GjX+QlghicBgQ/7bFaQZ+m5FKCMDnO+vTbNg96AF5H1K/siwSLK7RfstKtN5bAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglg");
              captcha.SetUrl("https://non-existent-example.execute-api.us-east-1.amazonaws.com");
              captcha.SetContext("test_iv");
              captcha.SetIV("test_context");
              try
              {
                  solver.Solve(captcha).Wait();
                  Console.WriteLine("Captcha solved: " + captcha.Code);
              }
              catch (AggregateException e)
              {
                  Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
              }
          }
      }
  }
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
    // https://github.com/2captcha/2captcha-java

    package examples;

    import com.twocaptcha.TwoCaptcha;
    import com.twocaptcha.captcha.AmazonWaf;

    public class AmazonWafExample {

        public static void main(String[] args) {
            TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");

            AmazonWaf captcha = new AmazonWaf();
            captcha.setSiteKey("AQIDAHjcYu/GjX+QlghicBgQ/7bFaQZ+m5FKCMDnO+vTbNg96AF5H1K/siwSLK7RfstKtN5bAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglg");
            captcha.setUrl("https://non-existent-example.execute-api.us-east-1.amazonaws.com");
            captcha.setIV("test_iv");
            captcha.setContext("test_context");

            try {
                solver.solve(captcha);
                System.out.println("Captcha solved: " + captcha.getCode());
            } catch (Exception e) {
                System.out.println("Error occurred: " + e.getMessage());
            }
        }

    }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
  // https://github.com/2captcha/2captcha-go
  package main

  import (
      "fmt"
      "log"
      "github.com/2captcha/2captcha-go"
  )

  func main() {
      client := api2captcha.NewClient("API_KEY")
      captcha := api2captcha.AmazonWAF{
      Iv: "CgAHbCe2GgAAAAAj",
      SiteKey: "0x1AAAAAAAAkg0s2VIOD34y5",
      Url: "https://non-existent-example.execute-api.us-east-1.amazonaws.com/latest",
      Context: "9BUgmlm48F92WUoqv97a49ZuEJJ50TCk9MVr3C7WMtQ0X6flVbufM4n8mjFLmbLVAPgaQ1Jydeaja94iAS49ljb",
      ChallengeScript: "https://41bcdd4fb3cb.610cd090.us-east-1.token.awswaf.com/41bcdd4fb3cb/0d21de737ccb/cd77baa6c832/challenge.js"
      CaptchaScript: "https://41bcdd4fb3cb.610cd090.us-east-1.captcha.awswaf.com/41bcdd4fb3cb/0d21de737ccb/cd77baa6c832/captcha.js",
      }
      code, err := client.Solve(captcha.ToRequest())
      if err != nil {
          log.Fatal(err);
      }
      fmt.Println("code "+code)
  }
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
  require 'api_2captcha'

  client =  Api2Captcha.new("YOUR_API_KEY")

  result = client.amazon_waf({
    sitekey: '0x1AAAAAAAAkg0s2VIOD34y5',
    iv: 'CgAHbCe2GgAAAAAj',
    context: '9BUgmlm48F92WUoqv97a49ZuEJJ50TCk9MVr3C7WMtQ0X6flVbufM4n8mjFLmbLVAPgaQ1Jydeaja94iAS49ljb+sUNLoukWedAQZKrlY4RdbOOzvcFqmD/ZepQFS9N5w15Exr4VwnVq+HIxTsDJwRviElWCdzKDebN/mk8/eX2n7qJi5G3Riq0tdQw9+C4diFZU5E97RSeahejOAAJTDqduqW6uLw9NsjJBkDRBlRjxjn5CaMMo5pYOxYbGrM8Un1JH5DMOLeXbq1xWbC17YSEoM1cRFfTgOoc+VpCe36Ai9Kc=',
    pageurl: 'https://non-existent-example.execute-api.us-east-1.amazonaws.com/latest',
    challenge_script: "https://41bcdd4fb3cb.610cd090.us-east-1.token.awswaf.com/41bcdd4fb3cb/0d21de737ccb/cd77baa6c832/challenge.js",
    captcha_script: "https://41bcdd4fb3cb.610cd090.us-east-1.captcha.awswaf.com/41bcdd4fb3cb/0d21de737ccb/cd77baa6c832/captcha.js"
  })
  ```
  </div>
</div>

## Useful links

* [How to bypass Amazon AWS captcha](/p/amazon-captcha-bypass)
* [Article about Amazon AWS captcha Bypass](https://2captcha.com/blog/amazon-captcha-solving)

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/siara-shield.svg" width="320" height="160" alt="CyberSiARA captcha" />

<h1>CyberSiARA</h1>

</div>

Token-based method for automated solving of `CyberSiARA`.

## Task types
- **AntiCyberSiAraTaskProxyless** - we use our own proxies pool to load and solve the captcha
- **AntiCyberSiAraTask** - we use your proxies

## Task specification

| Property             | Type     | Required  | Description  |
| -------------------- | -------- | --------- | ------------ |
| **type**             | *String* | **Yes**   | Task type: <br>**AntiCyberSiAraTask** <br>  **AntiCyberSiAraTaskProxyless**|
| **websiteURL**       | *String* | **Yes**   | The full URL of target web page where the captcha is loaded. |
| **SlideMasterUrlId** | *String* | **Yes**   | The value of the `MasterUrlId` parameter obtained from the request to the endpoint `API/CyberSiara/GetCyberSiara`.|
| **userAgent**        | *String* | **Yes**   | User-Agent of your browser will be used to load the captcha. Use only modern browser's User-Agents |


##  AntiCyberSiAraTask Task type specification

`AntiCyberSiAraTask` extends `AntiCyberSiAraTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |



## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`


### AntiCyberSiAraTaskProxyLess

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"AntiCyberSiAraTaskProxyless",
        "websiteURL":"https://www.cybersiara.com/book-a-demo",
        "SlideMasterUrlId":"OXR2LVNvCuXykkZbB8KZIfh162sNT8S2",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
}
```

### AntiCyberSiAraTask

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"AntiCyberSiAraTask",
        "websiteURL":"https://www.cybersiara.com/book-a-demo",
        "SlideMasterUrlId":"OXR2LVNvCuXykkZbB8KZIfh162sNT8S2",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "proxyType":"http",
        "proxyAddress":"1.2.3.4",
        "proxyPort":"8080",
        "proxyLogin":"user23",
        "proxyPassword":"p4$w0rd"
    }
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "eyJhbGciO...Tc4NTM3MQ=="
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/arkose.svg" width="320" height="160" alt="ArkoseLabs FunCaptcha widget" />

<h1>Arkose Labs captcha</h1>

</div>

Token-based method for automated solving of ArkoseLabs captcha (previously FunCaptcha).


## Task types
- **FunCaptchaTaskProxyless** - we use our own proxies pool to load and solve the captcha
- **FunCaptchaTask** - we use your proxies

## Task specification

| Property                 | Type     | Required | Description                                                         |
| ------------------------ | -------- | -------- | ------------------------------------------------------------------- |
| **type**                 | *String* | **Yes**  | Task type: <br>**FunCaptchaTaskProxyless** <br>  **FunCaptchaTask** |
| **websiteURL**           | *String* | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **websitePublicKey**     | *String* | **Yes**  | ArkoseLabs captcha public key. The public key can be found in the value of the `data-pkey` parameter of the `div` element FunCaptcha, or you can find an element named (name) `fc-token` and from its value cut out the key that is specified after `pk`.|
| funcaptchaApiJSSubdomain | *String* | No       | Custom subdomain used to load the captcha widget, like: `sample-api.arkoselabs.com` |
| data                     | *String* | No       | Additional data payload object converted to a string with `JSON.stringify`. Example: `{\"blob\":\"BLOB_DATA_VALUE\"}` |
| userAgent                | *String* | No       | User-Agent of your browser will be used to load the captcha. Use only modern browser's User-Agents |


## FunCaptchaTask Task type specification

`FunCaptchaTask` extends `FunCaptchaTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### FunCaptchaTaskProxyless

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"FunCaptchaTaskProxyless",
        "websiteURL":"https://www.example.com",
        "websitePublicKey":"6220FF23-9856-3A6F-9FF1-A14F88123F55",
        "funcaptchaApiJSSubdomain":"client-api.arkoselabs.com",
        "userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
}
```

### FunCaptchaTask

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"FunCaptchaTask",
        "websiteURL":"https://www.example.com",
        "websitePublicKey":"6220FF23-9856-3A6F-9FF1-A14F88123F55",
        "funcaptchaApiJSSubdomain":"client-api.arkoselabs.com",
        "userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "proxyType":"http",
        "proxyAddress":"1.2.3.4",
        "proxyPort":"8080",
        "proxyLogin":"user23",
        "proxyPassword":"p4$w0rd"
    }
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "142000f7f4545ca36.6123911001|r=us-beast-1|meta=3|metabgclr=%23ffffff|metaiconclr=%23757575|guitextcolor=%23000000|pk=6220FF23-9856-3A6F-9FF1-A14F88123F55|dc=1|at=40|ag=101|cdn_url=https%3A%2F%2Fsuncaptcha.com%2Fcdn%2Ffc|lurl=https%3A%2F%2Faudio-us-beast-1.arkoselabs.com|surl=https%3A%2F%2Fsuncaptcha.com|smurl=https%3A%2F%2Fsuncaptcha.com%2Fcdn%2Ffc%2Fassets%2Fstyle-manager"
    },
    "cost": "0.002",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 0
}
```


## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
  // https://github.com/2captcha/2captcha-php

  require(__DIR__ . '/../src/autoloader.php');

  $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

  try {
      $result = $solver->funcaptcha([
          'sitekey' => '6220FF23-9856-3A6F-9FF1-A14F88123F55',
          'url'     => 'https://www.example.com',
          'surl'      => 'https://client-api.arkoselabs.com',
      ]);
  } catch (\Exception $e) {
      die($e->getMessage());
  }

  die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
  # https://github.com/2captcha/2captcha-python

  # https://github.com/2captcha/2captcha-python

  import sys
  import os
  sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

  from twocaptcha import TwoCaptcha

  api_key = 'YOUR_API_KEY'

  solver = TwoCaptcha(api_key)

  try:
      result = solver.funcaptcha(sitekey='6220FF23-9856-3A6F-9FF1-A14F88123F55',
                                url='https://www.example.com',
                                surl='https://client-api.arkoselabs.com')

  except Exception as e:
      sys.exit(e)

  else:
      sys.exit('result: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
  // https://github.com/2captcha/2captcha-csharp

  using System;
  using System.Linq;
  using TwoCaptcha.Captcha;

  namespace TwoCaptcha.Examples
  {
      public class FunCaptchaExample
      {
          public void Main()
          {
              TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
              FunCaptcha captcha = new FunCaptcha();
              captcha.SetSiteKey("6220FF23-9856-3A6F-9FF1-A14F88123F55");
              captcha.SetUrl("https://www.example.com");
              captcha.SetSUrl("https://client-api.arkoselabs.com");
              try
              {
                  solver.Solve(captcha).Wait();
                  Console.WriteLine("Captcha solved: " + captcha.Code);
              }
              catch (AggregateException e)
              {
                  Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
              }
          }
      }
  }
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
  // https://github.com/2captcha/2captcha-java

  package examples;

  import com.twocaptcha.TwoCaptcha;
  import com.twocaptcha.captcha.FunCaptcha;

  public class FunCaptchaExample {
      public static void main(String[] args) {
          TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
          FunCaptcha captcha = new FunCaptcha();
              captcha.SetSiteKey("6220FF23-9856-3A6F-9FF1-A14F88123F55");
              captcha.SetUrl("https://www.example.com");
              captcha.SetSUrl("https://client-api.arkoselabs.com");
          try {
              solver.solve(captcha);
              System.out.println("Captcha solved: " + captcha.getCode());
          } catch (Exception e) {
              System.out.println("Error occurred: " + e.getMessage());
          }
      }
  }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
  // https://github.com/2captcha/2captcha-go
  package main

  import (
      "fmt"
      "log"
      "github.com/2captcha/2captcha-go"
  )

  func main() {
    client := api2captcha.NewClient("API_KEY")
    captcha := api2captcha.FunCaptcha{
      SiteKey: "6220FF23-9856-3A6F-9FF1-A14F88123F55",
      Url: "https://www.example.com",
      Surl: "https://client-api.arkoselabs.com",
      Data: map[string]string{"anyKey":"anyValue"},   
    }
      code, err := client.Solve(captcha.ToRequest())
      if err != nil {
          log.Fatal(err);
      }
      fmt.Println("code "+code)
  }
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
  require 'api_2captcha'

  client =  Api2Captcha.new("YOUR_API_KEY")

  result = client.funcaptcha({
  publickey: "6220FF23-9856-3A6F-9FF1-A14F88123F55",
  pageurl: "https://www.example.com",
  surl: "https://client-api.arkoselabs.com"
  })
  ```
  </div>
</div>

## Useful links

* [How to bypass Arkose Labs FunCaptcha](https://2captcha.com/p/funcaptcha)

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/atbcaptcha.svg" width="320" height="160" alt="atbCAPTCHA" />

<h1>atbCAPTCHA</h1>

</div>

Token-based method to bypass atbCAPTCHA.



## Task types
- **AtbCaptchaTaskProxyless** - we use our own pool of proxies
- **AtbCaptchaTask** - we use your proxies

## AtbCaptchaTaskProxyless task type specification

| Property                | Type     | Required | Description |
| ----------------------- | -------- | -------- | ----------- |
| **type**                | *String* | **Yes**  | Task type: <br>**AtbCaptchaTaskProxyless** <br>  **AtbCaptchaTask** |
| **websiteURL**          | *String* | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **appId**               | *String* | **Yes**  | The value of `appId` parameter in the website source code. |
| **apiServer**           | *String* | **Yes**  | The value of `apiServer` parameter in the website source code. |


## AtbCaptchaTask task type specification

`AtbCaptchaTask` extends `AtbCaptchaTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### AtbCaptchaTaskProxyless

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"AtbCaptchaTaskProxyless",
        "appId":"af23e041b22d000a11e22a230fa8991c",
        "apiServer":"https://cap.aisecurius.com",
        "websiteURL":"https://www.example.com/"
    }
}
```

### AtbCaptchaTask

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"AtbCaptchaTask",
        "appId":"af23e041b22d000a11e22a230fa8991c",
        "apiServer":"https://cap.aisecurius.com",
        "websiteURL":"https://www.example.com/",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": "8080",
        "proxyLogin": "user23",
        "proxyPassword": "p4$w0rd"
    }
}
```


## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "sl191suxzluwxxh6f:"
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

### Using the token

The token is passed to a callback function defined in `success` property during the captcha initialization. This function is usually used to make a request to the website backend where the token is verified. You can execute the callback function passing the token as an argument or build a request to the backend using passing the token.

```js
const myCallbackFunction = (token) {
    // verify the token
}
var myCaptcha = as.Captcha(document.getElementById('demo'), {
    appId: 'af23e041b22d000a11e22a230fa8991c', 
    success: myCallbackFunction
})
```




## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  </ul>


  <div id="python-code-example" data-component="TabPanel">

  ```python
  # https://github.com/2captcha/2captcha-python
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

solver = TwoCaptcha(api_key)

try:
    result = solver.atb_captcha(
        app_id='af23e041b22d000a11e22a230fa8991c',
        api_server='https://cap.aisecurius.com',
        url='http://www.example.com/',
    )

except Exception as e:
    sys.exit(e)

else:
    sys.exit('result: ' + str(result))
  ```
  </div>
</div>

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/audio.svg" width="320" height="160" alt="Audio" />

<h1>Audio captcha</h1>

</div>

We provide a speech recognition method that allows you to convert an audio record to text. The method can be used to bypass audio captchas or to recognize any audio record.

The limitations are:
* Max file size: `1 MB`
* Audio duration: `not limited`
* Supported audio format: `mp3 only`
* Supported speech languages: `English, French, German, Greek, Portuguese, Russian`

The recognition is fully automated and performed by a neural network trained for speech recognition.

## Task type: AudioTask

## AudioTask task type specification

| Property | Type     | Required | Default | Description                                                                     |
| -------- | -------- | -------- | ------- | ------------------------------------------------------------------------------- |
| **type** | *String* | **Yes**  |         | Task type: **AudioTask**                                                        |
| **body** | *String* | **Yes**  |         | Base64 encoded audio file in mp3 format                                         |
| lang     | *String* | **Yes**  | **en**  | The language of audio record. Supported languages are: `en`, `fr`, `de`, `el`, `pt`, `ru` |

### Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "AudioTask",
        "body": "R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==",
        "lang": "en"
    }
}
```

### Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "text": "hello world"
    },
    "cost": "0.0005",
    "ip": "1.2.3.4",
    "createTime": 1692808229,
    "endTime": 1692808326,
    "solveCount": 0
}
```

## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
    // https://github.com/2captcha/2captcha-php

    require(__DIR__ . '/../src/autoloader.php');

    $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

    try {
        $result = $solver->audio('path/to/audio.mp3');
    } catch (\Exception $e) {
        die($e->getMessage());
    }

    die('Captcha solved: ' . $result->code); 
```
  </div>



  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
    // https://github.com/2captcha/2captcha-csharp
    AudioCaptcha captcha = new AudioCaptcha();
    byte[] bytes = File.ReadAllBytes("../../resources/audio-en.mp3");
    string base64EncodedImage = Convert.ToBase64String(bytes);
    captcha.SetBase64(base64EncodedImage);
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
    // https://github.com/2captcha/2captcha-java
    TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
    byte[] bytes = Files.readAllBytes(Paths.get("src/main/resources/audio-en.mp3"));
    String base64EncodedImage = Base64.getEncoder().encodeToString(bytes);
    Audio captcha = new Audio();
    captcha.setBase64(base64EncodedImage);
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
    # https://github.com/2captcha/2captcha-ruby
    require 'api_2captcha'

    client =  Api2Captcha.new("YOUR_API_KEY")

    result = client.audio({
        audio: "path/to/audio.jpg",
        lang: "en"
    })
  ```
  </div>
</div>


## Useful links

* [Audio captcha solver: How to bypass audio reCAPTCHA and any other audio captcha](https://2captcha.com/blog/audio-captcha-solver)

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/basilisk-captcha.svg" width="320" height="160" alt="Basilisk" />

<h1>Basilisk captcha</h1>

</div>

This is a token based method to bypass Basilisk captcha.

## Task types
* **BasiliskTaskProxyless**. We use our own proxy pool to solve captchas.
* **BasiliskTask**. We use the proxy you provide.

## Specification for BasiliskTaskProxyless 

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| **type** | *String* | **Yes** | Task type. Choose BasiliskTaskProxyless or BasiliskTask. |
| **websiteURL** | *String* | **Yes** | Full URL of the target web page where the captcha is loaded. |
| **websiteKey** | *String* | **Yes** | Value of the data sitekey parameter found on the page. Unique for the website. |
| userAgent | *String* | No | Browser User Agent that opens the page. |

## Specification for BasiliskTask  

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| **proxyType** | *String* | **Yes** | Proxy type. Choose http, socks4, or socks5. |
| **proxyAddress** | *String* | **Yes** | IP address or hostname of the proxy server. |
| **proxyPort** | *Number* | **Yes** | Port of the proxy server. |
| proxyLogin | *String* | No | Login to authenticate on the proxy server. |
| proxyPassword | *String* | No | Password to authenticate on the proxy server. |

## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### Example request for BasiliskTaskProxyless

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
      "type": "BasiliskTaskProxyless",
      "websiteURL": "https://example.com/login",
      "websiteKey": "b7890hre5cf2...9c19fb2600897",
      "userAgent": "Mozilla/5.0 (Windows NT 10.0, Win64, x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
  }
```

### Example request for BasiliskTask with proxy

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
      "type": "BasiliskTask",
      "websiteUrl": "https://example.com/login",
      "websiteKey": "b7890h...19fb2600897",
      "userAgent": "Mozilla/5.0 (Windows NT 10.0, Win64, x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
      "proxyType": "http",
      "proxyAddress": "1.2.3.4",
      "proxyPort": 8080,
      "proxyLogin": "login",
      "proxyPassword": "password"
    }
  }
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
  "solution": {
    "data": {
      "captcha_response": "5620301f30daf...9fba66fa9b3d0"
    },
    "headers": {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0, Win64, x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
  }
}
```

You need to pass `captcha_response` to the target site as the Basilisk response. If the solution includes `headers.User-Agent`, use the same User Agent in your request to the site.

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/binance-captcha.svg" width="320" height="160" alt="Binance captcha" />

<h1>Binance captcha</h1>

</div>

Token-based method for automatic Binance captcha solving.

## Method specification
- **BinanceTaskproxyless** — we use our own proxy pool to solve captchas
- **BinanceTask** — we use your proxies

## BinanceTaskproxyless method specification

| Property         | Type       | Required | Description                                                  |
| -------------------- | --------  | -------- | -------------------------------------------------------- |
| **type**             | *String*  | **Yes**  | Task type: **BinanceTask** or **BinanceTaskproxyless**                   |
| **websiteURL**       | *String*  | **Yes**  | Full URL of the page where the captcha is loaded |
| **websiteKey**     | *String*  | **Yes**  | Value of `bizId`, `bizType`, or `bizCode` from page requests |
| **validateId**    | *String*  | **Yes**  | Dynamic value of `validateId`, `securityId`, or `securityCheckResponseValidateId` |

> **IMPORTANT**: some parameter values are dynamic — they change every time the Binance page is rendered.

## BinanceTask method specification


| Property         | Type       | Required | Description                                                  |
| ---------------- | --------- | ---------- | --------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**     | Proxy type: <br>**http** <br> **socks4** <br> **socks5**  |
| **proxyAddress** | *String*  | **Yes**     | Proxy server IP address or hostname                     |
| **proxyPort**    | *Integer*| **Yes**  | Proxy server port                                       |
| proxyLogin       | *String*  | No        | Login used for authentication on the proxy server     |
| proxyPassword    | *String*  | No        | Password used for authentication on the proxy server    |

## Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`


### BinanceTaskproxyless

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
      "type": "BinanceTaskproxyless",
      "websiteURL": "https://example.com/page-with-binance",
      "websiteKey": "login",
      "validateId": "cb0bfefa598...e54ecd57b",
      "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
  }
```
### BinanceTask

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
      "type": "BinanceTask",
      "websiteURL": "https://example.com/page-with-binance",
      "websiteKey": "login",
      "validateId": "cb0bfefa5...1fde54ecd57b",
      "proxyType": "http",
      "proxyAddress": "1.2.3.4",
      "proxyPort": 8080,
      "proxyLogin": "login",
      "proxyPassword": "password"
    }
  }
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
  "errorId": 0,
  "status": "ready",
  "solution": {
    "token": "captcha#09ba4905a79f44f...kc99maS943qIsquNP9D77",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
  }
}
```

## How to find `websiteKey` and `validateId`

Open developer tools, go to the Network tab, trigger the captcha and check the requests. Some of them will contain the parameter values you need.

Additionally, you can get the parameters needed for solving by running JavaScript:

```JavaScript
let originalBCaptcha = window.BCaptcha;
let BCaptchaData;

Object.defineProperty(window, 'BCaptcha', {
  get: function() {
    return function(args) {
      const BCaptcha = new originalBCaptcha(args);
      let BCaptchaShow = BCaptcha.__proto__.show;
      
      BCaptcha.__proto__.show = function(args) {
        BCaptchaData = args;
        return 1;
      };
      
      return BCaptcha;
    };
  }
});
```

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/bounding-box.svg" width="320" height="160" alt="Bounding Box image" />

<h1>Bounding Box Method</h1>

</div>

The method can be used to solve tasks where you need to select a specific object or draw a box around an object shown on an image.

**Supported image formats:** JPEG, PNG, GIF
**Max file size:** 600 kB
**Max image size:** 1000px on any side


## BoundingBoxTask task type specification

| Property        | Type     | Required | Description         |
| --------------- | -------- | -------- | ------------------- |
| **type**        | *String* | **Yes**  | **BoundingBoxTask** |
| **body**        | *String* | **Yes**  | Image encoded into Base64 format. Data-URI format (containing `data:content/type` prefix) is also supported |
| comment         | *String* | Yes*     | A comment will be shown to workers to help them to solve the captcha properly.<br>The `comment` property is required if the `imgInstructions` property is missing. |
| imgInstructions | *String* | Yes*     | An optional image with instruction that will be shown to workers. Image should be encoded into Base64 format. Max file size: 100 kB.<br>The `imgInstructions` property is required if the `comment` property is missing. |
| canNoAnswer     | *Integer* | No      | 0 - not specified<br>1 - possibly there's no objects that fit the instruction.<br>Set the value to 1 only if it's possible that there's no objects matching the instruction. We'll provide a button "No matching images" to worker and you will receive *No_matching_images* as answer. |


### Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"BoundingBoxTask",
        "body":"/9j/4AAQSkZJRgABAQAAAQ..HIAAAAAAQwAABtbnRyUkdCIFhZ.wc5GOGSRF//Z",
        "comment":"draw a tight box around the green apple"
    }
}
```

### Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "bounding_boxes": [
            {
                "xMin": 310,
                "xMax": 385,
                "yMin": 231,
                "yMax": 308
            }
        ]
    },
    "cost": "0.0012",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/captchafox.svg" width="320" height="160" alt="CaptchaFox" />

<h1>CaptchaFox</h1>

</div>

A token-based method for automatically solving `CaptchaFox` captchas.

To solve a `CaptchaFox` captcha, you must use a proxy and provide the `User-Agent` value of your browser.

> <b>Attention</b>: You must include the `proxy` parameters in your request. The proxy you provide will be used during captcha solving.

> <b>Attention</b>: You must include the `User-Agent` header used when accessing the target website. We use it during captcha loading and solving. Always use a `User-Agent` from a modern browser.

## Task Type
- **CaptchaFoxTask** – we will use the proxy you provide.


## CaptchaFoxTask  task type specification

| Property             | Type      | Required | Description                                              |
| -------------------- | --------  | -------- | -------------------------------------------------------- |
| **type**             | *String*  | **Yes**  | Task type: <br>**CaptchaFoxTask**                        |
| **websiteURL**       | *String*  | **Yes**  | The full URL of the target web page where the captcha is loaded. |
| **apiServer**        | *String*  | No       | Default: https://cdn.captchafox.com/. Depending on the parameter value, the token format changes — it will be prefixed with MAM_. For this, you need to set the server URL to: https://s.uicdn.com/mampkg/@mamdev/core.frontend.libs.captchafox/ Two different APIs return two different tokens. Choose the one you need. |
| **websiteKey**       | *String*  | **Yes**  | The value of the `key` parameter. It can be found in the page source code or captured in network requests during page loading. |
| **userAgent**        | *String*  | **Yes**  | The User-Agent of the browser that will be used by the worker to load the captcha. |
| **proxyType**        | *String*  | **Yes**  | Proxy type: <br>**http** <br>**socks4** <br>**socks5**    |
| **proxyAddress**     | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**        | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin           | *String*  | No       | Proxy login used for authentication on the proxy server  |
| proxyPassword        | *String*  | No       | Proxy password used for authentication on the proxy server |


## Request example

Method: [createTask](/api-docs/create-task)  
API endpoint: `https://api.2captcha.com/createTask`

### CaptchaFoxTask

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "CaptchaFoxTask",
    "websiteURL": "https://mysite.com/page/with/captchafox",
    "apiServer": "https://mam.example.com",
    "websiteKey": "sk_xtNxpk6fCdFbxh1_xJeGflSdCE9tn99G",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "proxyType": "http",
    "proxyAddress": "1.2.3.4",
    "proxyPort": "8080",
    "proxyLogin": "proxyUser123",
    "proxyPassword": "proxyPass456"
  }
}
```

### Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "7828075fb55ecbd9146745ee6f2bec475b88076d36e23050f1fb28359ffca15d"
    },
    "cost": "0.00145",
    "ip": "1.2.3.4",
    "createTime": 1695214711,
    "endTime": 1695214720,
    "solveCount": 1
}
```

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/capy.svg" width="320" height="160" alt="Capy widget" />

<h1>Capy Puzzle captcha</h1>

</div>

Token-based method for automated solving of Capy Puzzle Captcha.


## Task types
- **CapyTaskProxyless** - we use our own pool of proxies
- **CapyTask** - we use your proxies

## CapyTaskProxyless task type specification

| Property       | Type     | Required | Description |
| -------------- | -------- | -------- | ----------- |
| **type**       | *String* | **Yes**  | Task type: <br>**CapyTaskProxyless** <br>  **CapyTask** |
| **websiteURL** | *String* | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **websiteKey** | *String* | **Yes**  | Capy Puzzle Captcha `captchakey`. |
| userAgent      | *String* | No       | User-Agent of your browser will be used to load the captcha. Use only modern browser's User-Agents |


## CapyTask task type specification

`CapyTask` extends `CapyTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### CapyTask

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "CapyTask",
    "websiteURL": "https://example.com/",
    "websiteKey": "PUZZLE_Abc1dEFghIJKLM2no34P56q7rStu8v",
    "proxyType": "http",
    "proxyAddress": "1.2.3.4",
    "proxyPort": "8080",
    "proxyLogin": "user23",
    "proxyPassword": "p4$w0rd"
  }
}
```

### CapyTaskProxyless

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "CapyTaskProxyless",
    "websiteURL": "https://example.com/",
    "websiteKey": "PUZZLE_Abc1dEFghIJKLM2no34P56q7rStu8v"
  }
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "captchakey": "PUZZLE_Abc1dEFghIJKLM2no34P56q7rStu8v",
        "challengekey": "qHAPtn68KTnXFM8VQ3mtYRtmy3cSKuHJ",
        "answer": "0xax8ex0xax84x0xkx7qx0xux7gx0xx42x0x3ox42x0x3ox4cx",
        "respKey": ""
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```


## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
  // https://github.com/2captcha/2captcha-php
  $result = $solver->capy([
      'sitekey' => 'PUZZLE_Abc1dEFghIJKLM2no34P56q7rStu8v',
      'url'     => 'http://mysite.com/',
      'api_server' => 'https://jp.api.capy.me/',
  ]);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
  # https://github.com/2captcha/2captcha-python

  result = solver.capy(sitekey='PUZZLE_Abc1dEFghIJKLM2no34P56q7rStu8v',
                      url='http://mysite.com/',
                      api_server='https://jp.api.capy.me/',
                      param1=..., ...)
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
  // https://github.com/2captcha/2captcha-csharp

  Capy captcha = new Capy();
  captcha.SetSiteKey("PUZZLE_Abc1dEFghIJKLM2no34P56q7rStu8v");
  captcha.SetUrl("https://www.mysite.com/captcha/");
  captcha.SetProxy("HTTPS", "login:password@IP_address:PORT");
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
  // https://github.com/2captcha/2captcha-java
  Capy captcha = new Capy();
  captcha.setSiteKey("PUZZLE_Abc1dEFghIJKLM2no34P56q7rStu8v");
  captcha.setUrl("https://www.mysite.com/captcha/");
  captcha.setProxy("HTTPS", "login:password@IP_address:PORT");
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
  // https://github.com/2captcha/2captcha-go

  captcha := api2captcha.Capy{
    SiteKey: "PUZZLE_Abc1dEFghIJKLM2no34P56q7rStu8v",
    Url: "https://www.mysite.com/captcha/",
  }
  req := captcha.ToRequest()
  req.SetProxy("HTTPS", "login:password@IP_address:PORT")
  code, err := client.Solve(req)
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
  # https://github.com/2captcha/2captcha-ruby

  result = client.capy({
    sitekey: 'PUZZLE_Abc1dEFghIJKLM2no34P56q7rStu8v',
    pageurl: 'http://mysite.com/',
    api_server: 'https://jp.api.capy.me/'
  })
  ```
  </div>
</div>

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/cloudflare.svg" width="320" height="160" alt="Turnstile widget" />

<h1>Cloudflare Turnstile</h1>

</div>

Token-based method to bypass Cloudflare Turnstile. Both the standalone captcha and challenge mode are supported.


There are two different cases that require different approach:
- **Standalone Captcha** - the captcha widget is placed on a webiste page, see [our demo](/demo/cloudflare-turnstile)
- **Cloudflare Challenge page** - the captcha is shown on Cloudflare Challenge page


## Standalone Captcha
To bypass a standalone captcha you just need to find the `sitekey`, get a token from our API and then pass it to your target as a value of input element with name `cf-turnstile-response` or `g-recaptcha-response` for reCAPTCHA compatibility mode. Also the token can be processed with a callback function passed to `turnstile.render` call.


## Cloudflare Challenge page
This is much more complex case. You should intercept the `turnstile.render` call and grab the following values:
- `cData`
- `chlPageData`
- `action`

Also you will need to intercept the callback definition and use the userAgent returned from our API.

To intercept the required parameters you can inject the following JavaScript on page before the Turnstile widget is loaded.

```js
const i = setInterval(()=>{
if (window.turnstile) {
    clearInterval(i)
    window.turnstile.render = (a,b) => {
    let p = {
        type: "TurnstileTaskProxyless",
        websiteKey: b.sitekey,
        websiteURL: window.location.href,
        data: b.cData,
        pagedata: b.chlPageData,
        action: b.action,
        userAgent: navigator.userAgent
    }
    console.log(JSON.stringify(p))
    window.tsCallback = b.callback
    return 'foo'
    }
}
},10)  
```

An another approach is to intercept the request to `api.js` script and replace it with your own script that returns the parameters and makes the callback acessible globally.

Finally when you received the solution:
* execute the callback passing the token as it's argument
 

## Task types
- **TurnstileTaskProxyless** - we use our own pool of proxies
- **TurnstileTask** - we use your proxies

## TurnstileTaskProxyless task type specification

| Property          | Type      | Required | Description |
| ----------------- | --------- | -------- | ----------- |
| **type**          | *String*  | **Yes**  | Task type: <br>**TurnstileTaskProxyless** <br>  **TurnstileTask** |
| **websiteURL**    | *String*  | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users       |
| **websiteKey**    | *String*  | **Yes**  | Turnstile sitekey. Can be found inside `data-sitekey` property of the Turnstile `div` element |
| action            | *String*  | No*      | Required for Cloudflare Challenge pages. The value of `action` parameter of `turnstile.render` call |
| data              | *String*  | No*      | Required for Cloudflare Challenge pages. The value of `cData` parameter of `turnstile.render` call |
| pagedata          | *String*  | No*      | Required for Cloudflare Challenge pages. The value of `chlPageData` parameter of `turnstile.render` call |


## TurnstileTask task type specification

`TurnstileTask` extends `TurnstileTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### Standalone Captcha

#### TurnstileTaskProxyless request example

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"TurnstileTaskProxyless",
        "websiteURL":"https://2captcha.com/demo/cloudflare-turnstile",
        "websiteKey":"3x00000000000000000000FF"
    }
}
```


#### TurnstileTask request example

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"TurnstileTask",
        "websiteURL":"https://2captcha.com/demo/cloudflare-turnstile",
        "websiteKey":"3x00000000000000000000FF",
        "proxyType":"http",
        "proxyAddress":"1.2.3.4",
        "proxyPort":"8080",
        "proxyLogin":"user23",
        "proxyPassword":"p4$w0rd"
    }
}
```

### Cloudflare Challenge Pages

#### TurnstileTaskProxyless request example

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"TurnstileTaskProxyless",
        "websiteURL":"https://2captcha.com/demo/cloudflare-turnstile",
        "websiteKey":"3x00000000000000000000FF",
        "action": "managed",
        "data": "80001aa1affffc21",
        "pagedata": "3gAFo2l...55NDFPRFE9"
    }
}
```


#### TurnstileTask request example

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"TurnstileTask",
        "websiteURL":"https://2captcha.com/demo/cloudflare-turnstile",
        "websiteKey":"3x00000000000000000000FF",
        "action": "managed",
        "data": "80001aa1affffc21",
        "pagedata": "3gAFo2l...55NDFPRFE9",
        "proxyType":"http",
        "proxyAddress":"1.2.3.4",
        "proxyPort":"8080",
        "proxyLogin":"user23",
        "proxyPassword":"p4$w0rd"
    }
}
```


### Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "0.zrSnRHO7h0HwSjSCU8oyzbjEtD8p.d62306d4ee00c77dda697f959ebbd7bd97",
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    },
    "cost": "0.00145",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
  // https://github.com/2captcha/2captcha-php

  require(__DIR__ . '/../src/autoloader.php');

  $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

  try {
      $result = $solver->turnstile([
          'sitekey' => '3x00000000000000000000FF',
          'url'     => 'https://2captcha.com/demo/cloudflare-turnstile',
      ]);
  } catch (\Exception $e) {
      die($e->getMessage());
  }
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
  # https://github.com/2captcha/2captcha-python

  import sys
  import os

  sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

  from twocaptcha import TwoCaptcha

  api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

  solver = TwoCaptcha(api_key)

  try:
      result = solver.turnstile(
          sitekey='3x00000000000000000000FF',
          url='https://2captcha.com/demo/cloudflare-turnstile',
      )

  except Exception as e:
      sys.exit(e)

  else:
      sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```ruby
  require 'api_2captcha'

  client =  Api2Captcha.new("YOUR_API_KEY")

  result = client.turnstile({
  sitekey: '3x00000000000000000000FF',
  pageurl: 'https://2captcha.com/demo/cloudflare-turnstile'
  })
  ```
  </div>
</div>


## Useful links

* [Turnstile demo page](/demo/cloudflare-turnstile)
* [How to bypass Turnstile](/p/cloudflare-turnstile)
* [Video how to bypass Turnstile](https://youtu.be/ZoSWMgNwfuM)
* [Turnstile on Cloudflare Challenge pages](/blog/bypass-cloudflare-turnstile-captcha)

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/coordinates.svg" width="320" height="160" alt="Coordinates" />

<h1>Coordinates Method</h1>

</div>

The method can be used to bypass tasks where you need to click on some points of an image.

The method can be also used for cases when you need to calculate a distance between points. For example, to bypass custom slider captchas you can instruct our worker to click on a particular point of the image using `comment` and `imgInstructions` parameters and then use the point coordinates to calculate the distance between the slider start and end points and move the slider.

**Supported image formats:** JPEG, PNG, GIF
**Max file size:** 600 kB
**Max image size:** 1000px on any side


## CoordinatesTask task type specification

| Property        | Type     | Required | Description |
| --------------- | -------- | -------- | ----------- |
| **type**        | *String* | **Yes**  | Task type: **CoordinatesTask** |
| **body**        | *String* | **Yes**  | Image encoded into Base64 format. Data-URI format (containing `data:content/type` prefix) is also supported |
| comment         | *String* | No       | A comment will be shown to workers to help them to solve the captcha properly |
| imgInstructions | *String* | No       | An optional image with instruction that will be shown to workers. Image should be encoded into Base64 format. Max file size: 100 kB |
| minClicks       | *Integer* | No      | The minimum number of clicks to perform on the image. Default: `1` |
| maxClicks       | *Integer* | No      | The maximum number of clicks that can be performed on the image |


### Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"CoordinatesTask",
        "body":"/9j/4AAQSkZJRgABAQAAAQ..HIAAAAAAQwAABtbnRyUkdCIFhZ.wc5GOGSRF//Z",
        "comment":"click on the green apple"
    }
}
```

### Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "coordinates": [
            {
                "x": 358,
                "y": 268
            }
        ]
    },
    "cost": "0.0012",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
    // https://github.com/2captcha/2captcha-php

    require(__DIR__ . '/../src/autoloader.php');

    $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

    try {
        $result = $solver->coordinates('path/to/captcha.jpg');
    } catch (\Exception $e) {
        die($e->getMessage());
    }

    die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
# https://github.com/2captcha/2captcha-python

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

solver = TwoCaptcha(api_key)

try:
    result = solver.coordinates('path/to/captcha.jpg')

except Exception as e:
    sys.exit(e)

else:
    sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
    // https://github.com/2captcha/2captcha-csharp

    using System;
    using System.Linq;
    using TwoCaptcha.Captcha;

    namespace TwoCaptcha.Examples
    {
        public class CoordinatesExample
        {
            public static void Main()
            {
                var solver = new TwoCaptcha("YOUR_API_KEY");
                Coordinates captcha = new Coordinates("path/to/captcha.jpg");
                try
                {
                    solver.Solve(captcha).Wait();
                    Console.WriteLine("Captcha solved: " + captcha.Code);
                }
                catch (AggregateException e)
                {
                    Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
                }
            }
        }
    }
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
    // https://github.com/2captcha/2captcha-java

    package examples;

    import com.twocaptcha.TwoCaptcha;
    import com.twocaptcha.captcha.Coordinates;

    public class CoordinatesExample {
        public static void main(String[] args) {
            TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
            Coordinates captcha = new Coordinates("path/to/captcha.jpg");
            try {
                solver.solve(captcha);
                System.out.println("Captcha solved: " + captcha.getCode());
            } catch (Exception e) {
                System.out.println("Error occurred: " + e.getMessage());
            }
        }

    }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
    // https://github.com/2captcha/2captcha-go

    package main

    import (
        "fmt"
        "log"
        "github.com/2captcha/2captcha-go"
    )

    func main() {
        client := api2captcha.NewClient("API_KEY")
        captcha := api2captcha.Coordinates{
            File: "/path/to/captcha.jpg",
        }
        code, err := client.Solve(captcha.ToRequest())
        if err != nil {
            log.Fatal(err);
        }
        fmt.Println("code "+code)
    }
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
    require 'api_2captcha'

    client =  Api2Captcha.new("YOUR_API_KEY")

    result = client.coordinates({ image: 'path/to/captcha.jpg'})
    # OR
    result = client.coordinates({
    image: 'https://site-with-captcha.com/path/to/captcha.jpg'
    })
  ```
  </div>
</div>


## Useful links

* [Demo page ClickCaptcha](https://2captcha.com/demo/clickcaptcha)

---

# createTask method

The method is used to create a new captcha recognition task for a selected captcha task type. Returns the `id` of the task or an [error code](/api-docs/error-codes)

**API Endpoint:** `https://api.2captcha.com/createTask`
**Method:** `POST`
**Content-Type:** `application/json`

## Request properties

| Name          | Type      | Required | Description                |
| ------------- | --------- | -------- | -------------------------- |
| **clientKey** | *String*  | **Yes**  | Your [API key](/enterpage) |
| **task**      | *Object*  | **Yes**  | Task object, see [`Captcha task types`](/api-docs) |
| languagePool  | *String*  | No       | Used to choose the workers for solving the captcha by their language. Applicable to image-based and text-based captchas. <br> Default: `en`. <br> `en` - English-speaking workers <br> `ru` - Russian-speaking workers. |
| callbackUrl   | *String*  | No       | URL of your web [registered web server](/setting/pingback) used to receive and process the captcha resolution result                                                                                                    |
| softId        | *Integer* | No       | The ID of your software registered in our [Software catalog](/software) |

## Request example

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"RecaptchaV2TaskProxyless",
        "websiteURL":"https://2captcha.com/demo/recaptcha-v2",
        "websiteKey":"6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u"
    }
}
```

## Response example

```json
{
    "errorId": 0,
    "taskId": 72345678901
}
```


<!--

### Code examples

<details>
<summary>cURL</summary>

```bash
curl --location 'https://api.2captcha.com.com/createTask' \
--header 'Content-Type: application/json' \
--data '{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"RecaptchaV2TaskProxyless",
        "websiteURL":"https://2captcha.com/demo/recaptcha-v2",
        "websiteKey":"6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u"
    }
}'
```
</details>

<details>
<summary>Node.js (request)</summary>

```javascript
const request = require('request');
const options = {
  'method': 'POST',
  'url': 'https://api.2captcha.com.com/createTask',
  'headers': {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    "clientKey": "YOUR_API_KEY",
    "task": {
      "type": "RecaptchaV2TaskProxyless",
      "websiteURL": "https://2captcha.com/demo/recaptcha-v2",
      "websiteKey": "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u"
    }
  })
};
request(options, function (error, response) {
  if (error) throw new Error(error);
  console.log(response.body);
});
```
</details>


<details>
<summary>PHP cURL</summary>

```php
<?php

$curl = curl_init();

curl_setopt_array($curl, array(
  CURLOPT_URL => 'https://api.2captcha.com.com/createTask',
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_ENCODING => '',
  CURLOPT_MAXREDIRS => 10,
  CURLOPT_TIMEOUT => 0,
  CURLOPT_FOLLOWLOCATION => true,
  CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
  CURLOPT_CUSTOMREQUEST => 'POST',
  CURLOPT_POSTFIELDS =>'{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"RecaptchaV2TaskProxyless",
        "websiteURL":"https://2captcha.com/demo/recaptcha-v2",
        "websiteKey":"6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u"
    }
}',
  CURLOPT_HTTPHEADER => array(
    'Content-Type: application/json'
  ),
));

$response = curl_exec($curl);

curl_close($curl);
echo $response;

```
</details>



<details>
<summary>Python (requests)</summary>

```python
import requests
import json

url = "https://api.2captcha.com/createTask"

payload = json.dumps({
  "clientKey": "1326ce1386fc2db6f75a1c69387645b8",
  "task": {
    "type": "RecaptchaV2TaskProxyless",
    "websiteURL": "https://2captcha.com/demo/recaptcha-v2",
    "websiteKey": "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u"
  }
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
```
</details>

-->

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/cutcaptcha.svg" width="320" height="160" alt="Cutcaptcha" />

<h1>Cutcaptcha</h1>

</div>

Token-based method to bypass Cutcaptcha.

The token received must be set as the `value` attribute of the `input#cap_token` element and/or passed to the callback function.

## Task types
- **CutCaptchaTaskProxyless** - we use our own pool of proxies
- **CutCaptchaTask** - we use your proxies

## CutCaptchaTaskProxyless task type specification

| Property                | Type     | Required | Description |
| ----------------------- | -------- | -------- | ----------- |
| **type**                | *String* | **Yes**  | Task type: <br>**CutCaptchaTaskProxyless** <br>  **CutCaptchaTask** |
| **websiteURL**          | *String* | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **miseryKey**           | *String* | **Yes**  | The value of `CUTCAPTCHA_MISERY_KEY` variable defined on page. |
| **apiKey**              | *String* | **Yes**  | The value of `data-apikey` attribute of iframe's body. Also the name of javascript file included on the page |


## CutCaptchaTask task type specification

`CutCaptchaTask` extends `CutCaptchaTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### CutCaptchaTaskProxyless

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "CutCaptchaTaskProxyless",
        "miseryKey": "a1488b66da00bf332a1488993a5443c79047e752",
        "apiKey": "SAb83IIB",
        "websiteURL": "https://example.cc/foo/bar.html"
    }
}
```

### CutCaptchaTask

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "CutCaptchaTask",
        "miseryKey": "a1488b66da00bf332a1488993a5443c79047e752",
        "apiKey": "SAb83IIB",
        "websiteURL": "https://example.cc/foo/bar.html",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": "8080",
        "proxyLogin": "user23",
        "proxyPassword": "p4$w0rd"
    }
}
```


## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "BazM23cpFUUyAAAdqPwNEDZx0REtH3ss"
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

### Using the token

Use the returned token as a value for  `input` with `id = cap_token`, then submit it's parent form, for example:

```js
document.querySelector('input#cap_token').value='BazM23cpFUUyAAAdqPwNEDZx0REtH3ss'
document.querySelector('form').submit()
```

If there's a callback function defined, you can call it passing the token as argument:

```js
capResponseCallback('BazM23cpFUUyAAAdqPwNEDZx0REtH3ss')
```

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/datadome-captcha.svg" width="320" height="160" alt="DataDome" />

<h1>DataDome captcha</h1>

</div>

Token-based method for automated solving of `DataDome`.

To solve the `DataDome` captcha, you must use a proxy.

> <b>Attention</b>, you need to check the value of the parameter `t` in `captchaUrl` if it is contained. The value of `t` must be equal to `fe`.
> If `t=bv`, it means that your ip is banned by the captcha and you need to change the ip address.

> <b>Attention</b>, you must monitor the quality of the proxy used. If your proxy is blocked by the `DataDome` you will receive errors `ERR_PROXY_CONNECTION_FAILED` or `ERROR_CAPTCHA_UNSOLVABLE`, in such cases you need to rotate the proxy. You can use [redidential proxies](/proxy) provided by our serivce.

> <b>Attention</b>, you should provide your User-Agent that was used to interact with target website, it will be used to load and solve the captcha. Always use User-Agents of modern browsers.

## Task type
- **DataDomeSliderTask** - we use your proxies

## DataDomeSliderTask  task type specification

| Property             | Type      | Required | Description                                              |
| -------------------- | --------  | -------- | -------------------------------------------------------- |
| **type**             | *String*  | **Yes**  | Task type: **DataDomeSliderTask**                        |
| **websiteURL**       | *String*  | **Yes**  | The full URL of target web page where the captcha is loaded. |
| **captchaUrl**       | *String*  | **Yes**  | The value of the `src` parameter for the `iframe` element containing the captcha on the page. |
| **userAgent**        | *String*  | **Yes**  | User-Agent of your browser will be used to load the captcha. |
| **proxyType**        | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress**     | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**        | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin           | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword        | *String*  | No       | Password for basic authentication on the proxy           |


## Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`


### DataDomeSliderTask

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "DataDomeSliderTask",
    "websiteURL": "https://www.pokemoncenter.com/",
    "captchaUrl": "https://geo.captcha-delivery.com/captcha/?initialCid=AHrlqAAAAAMAlk-FmAyNOW8AUyTH_g%3D%3D&hash=5B45875B653A484CC79E57036CE9FC&cid=noJuZstmvINksqOxaXWQogbPBd01y3VaH3r-CZ4eqK4roZuelJMHVhO2rR0IySRieoAivkg74B4UpJ.xj.jVNB6-aLaW.Bwvik7__EncryD6COavwx8RmOqgZ7DK_3v&t=fe&referer=https%3A%2F%2Fwww.pokemoncenter.com%2F&s=9817&e=2b1d5a78107ded0dcdc8317aa879979ed5083a2b3a95b734dbe7871679e1403",
    "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.3",
    "proxyType":"http",
    "proxyAddress":"1.2.3.4",
    "proxyPort": "8080",
    "proxyLogin":"user23",
    "proxyPassword":"p4$w0rd"
  }
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "cookie": "datadome=4ZXwCBlyHx9ktZhSnycMF...; Path=/; Secure; SameSite=Lax"
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1695214711,
    "endTime": 1695214720,
    "solveCount": 1
}
```

---

# Debugging & Sandbox

If you have a doubt integrating your software with our API and need to debug your code and API requests we provide some instruments and suggestions to help you on that.

## Method *test*

The method allows to check the parameters of your request and see how our API service sees your request.

Use it if you receive an [error code](/api-docs/error-codes) from our API and can not understand what are you doing wrong. Just replace the API enpoint from `createTask` or `getResponse` to `test` and compare the parameters you sent with the returned values. 

**API Endpoint:** `https://api.2captcha.com/test`
**Method:** `POST`
**Content-Type:** `application/json`

### Request example

```json
{
    "clientKey": "YOUR_API_KEY",
    "foo": "bar",
    "test": true,
    "attempt": 3,
    "options": {
        "list": [
            "item1",
            "item2"
        ]
    }
}
```

### Response example

```
Parsed input JSON:
Dict
(
[clientKey] => YOUR_API_KEY
[foo] => bar
[test] => 1
[attempt] => 3
[options] => Dict
(
[list] => Dict
(
[0] => item1
[1] => item2
)

)

)
Raw POST input:
{
"clientKey": "YOUR_API_KEY",
"foo": "bar",
"test": true,
"attempt": 3,
"options": {
"list": [
"item1",
"item2"
]
}
}
```


## Sandbox mode

We also provide the `sandbox` that allows you to see how our workers will see your tasks.
Sandbox can be really useful for cases when our workers can not solve your captcha or you receive incorrect answers.

To debug a captcha in Sandbox follow these simple steps:
- enable [sandbox mode](/setting#sandbox)
- if you need to debug image-based captchas go directly to [workers' cabinet](/cabinet)
- if you need to debug an interactive captcha:
  1. download our [workers' software](/support/workers-software)
  2. get your `Client KEY` for the `worker` role. To do this, switch the role you are using to `worker` in [cabinet](/enterpage).
  3. log in to the installed application using `Client KEY` 
 for role `worker`.
- submit your captcha to the API and try to solve it 

## Browser automation issues

There's a really common problem with executing JavaScript, especially callbacks from browser automation framework. Most of the problems are caused by simple syntax errors when you need to pass some JavaScript, substitute some variables and pass arguments to JavaScript function calls.

We always recommend the following approach for such kind of tasks:
1. Try to solve the captcha manually on the website to ensure that it really works. There are cases when website administrators deploy the captcha incorrectly or just forget to pay the captcha service bills and the captcha does not work at all, so it can not be solved.
2. Try to bypass the captcha executing the JavaScript manually in the browser console. This really helps to understand how your call should look like.
3. Only when two previous steps were successul, start to automate with the code in your favourive language using your prefered frameworks.

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/drag-and-drop.svg" width="320" height="160" alt="Drag & Drop" />

<h1>Drag & Drop Method</h1>

</div>

The method can be used to bypass tasks where you need to drag one or more images onto specific positions on a background image.

## DragAndDropTask specification

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| **type** | *String* | **Yes** | Task type: **DragAndDropTask** |
| **background** | *String* | **Yes** | Background image encoded into Base64 format |
| **images** | *Array of String* | **Yes** | Array of images to drag, encoded into Base64 format. Order matters — the same order is used in the response |
| comment | *String* | No | A comment shown to workers to help them solve the captcha properly, e.g. "Drag the images to proper position" |

## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### DragAndDropTask request example

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "DragAndDropTask",
        "background": "BASE64_BACKGROUND",
        "images": [
            "BASE64_IMAGE_1",
            "BASE64_IMAGE_2"
        ],
        "comment": "Drag the images to proper position"
    }
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "coordinates": [
            {"x": 120, "y": 340},
            null,
            {"x": 210, "y": 90}
        ]
    },
    "cost": "0.0012",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

> **IMPORTANT**: `null` in `solution.coordinates` is a literal value for an image that wasn't moved — it does **not** mean an error and does **not** mean coordinates `(0, 0)`. The position of `null` in the array still corresponds to the position of that image in the `images` array you sent, so `solution.coordinates` always has the same length and order as the `images` array.

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/draw-around.svg" width="320" height="160" alt="Draw Around image" />

<h1>Draw Around Method</h1>

</div>

The method can be used to bypass tasks where you need to draw a line around a specific object shown on an image.

**Supported image formats:** JPEG, PNG, GIF
**Max file size:** 600 kB
**Max image size:** 1000px on any side


## DrawAroundTask task type specification

| Property        | Type      | Required | Description        |
| --------------- | --------- | -------- | ------------------ |
| **type**        | *String*  | **Yes**  | **DrawAroundTask** |
| **body**        | *String*  | **Yes**  | Image encoded into Base64 format. Data-URI format (containing `data:content/type` prefix) is also supported |
| comment         | *String* | Yes*     | A comment will be shown to workers to help them to solve the captcha properly.<br>The `comment` property is required if the `imgInstructions` property is missing. |
| imgInstructions | *String* | Yes*     | An optional image with instruction that will be shown to workers. Image should be encoded into Base64 format. Max file size: 100 kB.<br>The `imgInstructions` property is required if the `comment` property is missing. |

### Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"DrawAroundTask",
        "body":"/9j/4AAQSkZJ...OGSRF//Z",
        "comment":"draw around an apple"
    },
    "languagePool":"en"
}
```

### Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "canvas": [
            [
                {
                    "x": 141,
                    "y": 93
                },
                {
                    "x": 145,
                    "y": 93
                }
            ],
            [
                {
                    "x": 350,
                    "y": 263
                },
                {
                    "x": 350,
                    "y": 263
                }
            ],
            [
                {
                    "x": 350,
                    "y": 263
                }
            ]
        ]
    },
    "cost": "0.0012",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 0
}
```

---

# Error codes

## API error codes reference

In case if something is wrong with your request or task our API returns an error code. Below you can find the full list of our API error codes.

| Id  | Code                           | Description |
| --- | ------------------------------ | ----------- |
| 0   | -                              | No errors   |
| 1   | ERROR_KEY_DOES_NOT_EXIST       | Your API key is incorrect. Make sure you set the key correctly and copied it from the [dashboard](/enterpage) in *Customer* or *Developer* mode |
| 2   | ERROR_NO_SLOT_AVAILABLE        | Your bid is too low for the captcha you submit or the queue of your captchas is loo long and we temporary do not accept more captchas from you |
| 3   | ERROR_ZERO_CAPTCHA_FILESIZE    | Image size is less than 100 bytes |
| 4   | ERROR_TOO_BIG_CAPTCHA_FILESIZE | Image size is more than 100 kB or image is bigger than 600px on any side |
| 5   | ERROR_PAGEURL                  | The value of `websiteURL` parameter is missing or has incorrect format. Set it to the page url value |
| 10  | ERROR_ZERO_BALANCE             |  You don't have funds on your account |
| 11  | ERROR_IP_NOT_ALLOWED           | The request is sent from the IP that is not on the list of your [trusted IPs](/setting/iplist) | 
| 12  | ERROR_CAPTCHA_UNSOLVABLE       | We are unable to solve your captcha - three of our workers were unable solve it. The captcha price is automatically returned to your balance |
| 13  | ERROR_BAD_DUPLICATES           | The error is returned when [100% accuracy feature](/setting/percent_100) is enabled. The error means that max numbers of tries is reached but min number of matches not found |
| 14  | ERROR_NO_SUCH_METHOD           | Request made to API with a method that does not exist |
| 15  | ERROR_IMAGE_TYPE_NOT_SUPPORTED | The image can not be processed due to an incorrect format or size, or the image is corrupted. Please check the image in your request payload |
| 16  | ERROR_NO_SUCH_CAPCHA_ID        | You've provided incorrect captcha ID in the request |
| 21  | ERROR_IP_BLOCKED               | Your IP address is banned due to improper use of the API |
| 22  | ERROR_TASK_ABSENT              | `task` property is missing in your [`createTask`](/api-docs/create-task) method call |
| 23  | ERROR_TASK_NOT_SUPPORTED       | `task` property in your [`createTask`](/api-docs/create-task) method call contains the type of task that is not supported by our API or you have an error in `type` property |
| 31  | ERROR_RECAPTCHA_INVALID_SITEKEY| The `sitekey` value provided in your request is not valid |
| 55  | ERROR_ACCOUNT_SUSPENDED        | Your API access was blocked for improper use of the API. Please contact our support team to resolve the issue |
| 130 | ERROR_BAD_PROXY                | Incorrect proxy parameters or can not establish connection through the proxy |
| 110 | ERROR_BAD_PARAMETERS           | The required captcha parameters in your reques are missing or have incorrect format. Please make sure your request payload has proper format for selected task type |
| 115 | ERROR_BAD_IMGINSTRUCTIONS | The error is returned in cases when `imgInstructions` contains unsupported file type, corrupted file or the size of the image is over the limits. The limits are described in the corresponding task type specification. |


## HTTP response codes

If our API is able to process your requests properly the response status code is always [`200 OK`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200). But in case if there are any kind of technical issue, a failure or maintanence, your request can receive an [error response](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#server_error_responses) or for a malformed request you can receive a [client error response](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses). We recommend you to check the status code for every response and if it is not [`200 OK`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200) then wait few seconds and repeat the request. You can also log your request data and the response for debugging purposes, this info can be useful when [contacting our support team](/support/tickets/new).

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/friendly-captcha.svg" width="320" height="160" alt="Friendly Captcha" />

<h1>Friendly Captcha</h1>

</div>

Token-based method to bypass Friendly Captcha.

The token received must be set as the `value` attribute of the input element with name `frc-captcha-solution`  and/or passed to the callback function defined in `data-callback` attribute of the captcha div.

> **Important:** To successfully use the received token, the captcha widget must not be loaded on the page. To do this, you need to abort request to `/friendlycaptcha/...module.min.js` on the page. When the captcha widget is already loaded on the page, there is a high probability that the received token will not work.

## Task types
- **FriendlyCaptchaTaskProxyless** - we use our own pool of proxies
- **FriendlyCaptchaTask** - we use your proxies

## FriendlyCaptchaTaskProxyless task type specification

| Property                | Type     | Required | Description |
| ----------------------- | -------- | -------- | ----------- |
| **type**                | *String* | **Yes**  | Task type: <br>**FriendlyCaptchaTaskProxyless** <br>  **FriendlyCaptchaTask** |
| **websiteURL**          | *String* | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **websiteKey**           | *String* | **Yes**  | The value of `data-sitekey` attribute of captcha's `div` element on page. |
| **version**              | *String* | No       | Friendly Captcha version.<br>`v1` — Friendly Captcha v1.<br>`v2` — Friendly Captcha v2.<br> Default: `v1`.<br>See the official Friendly Captcha documentation for more details on the differences between v1 and v2. |
| **moduleScript**         | *String* | No       | URL of the **Friendly Captcha** script with `type="module"` attribute, found on the captcha page. |
| **nomoduleScript**       | *String* | No       | URL of the **Friendly Captcha** script with `nomodule` attribute, found on the captcha page. |


## FriendlyCaptchaTask task type specification

`FriendlyCaptchaTask` extends `FriendlyCaptchaTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### FriendlyCaptchaTaskProxyless

Friendly Captcha v1:
```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "FriendlyCaptchaTaskProxyless",
        "websiteURL": "https://example.com",
        "websiteKey": "2FZFEVS1FZCGQ9",
        "version": "v1",
        "moduleScript": "https://cdn.example.com/static/js/friendly-challenge/@0.9.1/widget.module.min.js",
        "nomoduleScript": "https://cdn.example.com/static/js/friendly-challenge/@0.9.1/widget.js"
    }
}
```

Friendly Captcha v2:
```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "FriendlyCaptchaTaskProxyless",
        "websiteURL": "https://example.com",
        "websiteKey": "2FZFEVS1FZCGQ9",
        "version": "v2",
        "moduleScript": "https://cdn.example.com/v2/widget.module.min.js",
        "nomoduleScript": "https://cdn.example.com/v2/widget.js"
    }
}
```

### FriendlyCaptchaTask

Friendly Captcha v1:
```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "FriendlyCaptchaTask",
        "websiteURL": "https://example.com",
        "websiteKey": "2FZFEVS1FZCGQ9",
        "version": "v1",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": "8080",
        "proxyLogin": "user23",
        "proxyPassword": "p4$w0rd",
        "moduleScript": "https://cdn.example.com/static/js/friendly-challenge/@0.9.1/widget.module.min.js",
        "nomoduleScript": "https://cdn.example.com/static/js/friendly-challenge/@0.9.1/widget.js"
    }
}
```

Friendly Captcha v2:
```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "FriendlyCaptchaTask",
        "websiteURL": "https://example.com",
        "websiteKey": "2FZFEVS1FZCGQ9",
        "version": "v2",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": "8080",
        "proxyLogin": "user23",
        "proxyPassword": "p4$w0rd",
        "moduleScript": "https://cdn.example.com/v2/widget.module.min.js",
        "nomoduleScript": "https://cdn.example.com/v2/widget.js"
    }
}
```


## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "f8b10f4ad796484bae963b1ebe3ce2bb.ZXL8Z...AAAAAA.AgAD"    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

### Using the token

Use the returned token as a value for  `input` with `name = frc-captcha-solution`, then submit it's parent form, for example:

```js
document.querySelector('input.frc-captcha-solution').value='f8b10f4ad796484bae963b1ebe3ce2bb.ZXL8Z...AAAAAA.AgAD'
document.querySelector('form').submit()
```

Please note, that form name can be customized with `data-solution-field-name` attribute, then you need to use the name set as the attribute's value.


If there's a callback function defined, you can call it passing the token as argument. For example, if `data-callback="doneCallback"` you should run it as:

```js
doneCallback('f8b10f4ad796484bae963b1ebe3ce2bb.ZXL8Z...AAAAAA.AgAD')
```

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/arkose.svg" width="320" height="160" alt="FunCaptcha Grid widget" />

<h1>FunCaptcha Grid (Image Click)</h1>

</div>

<div>

This type of FunCaptcha requires selecting grid cells that match the given instruction (for example, *"Select all images with arrows pointing to the right"*).

Although image-based FunCaptcha also has a [separate API method](/2captcha-api#solving_funcaptcha_new) based on tokens, it can also be solved via the universal **Grid method**.

The captcha image is divided into equal parts, and the solution result is returned as a list of cell numbers to click.

</div>

Returns an array of selected tile indexes, where 0 corresponds to the top-left corner of the grid.

* Supported image formats: JPEG, PNG, GIF
* Maximum file size: 600 kB
* Maximum image size: 1000px on any side

## GridTask Specification (FunCaptcha)

| Property        | Type      | Required | Description |
| --------------- | -------- | -------- | ----------- |
| **type**        | *String* | **Yes**  | Task type: **GridTask** |
| **body**        | *String* | **Yes**  | Base64-encoded image. Data-URI format (with `data:content/type` prefix) is also supported |
| rows            | *Number* | No       | Number of rows in the grid |
| columns         | *Number* | No       | Number of columns in the grid |
| comment         | *String* | **Yes\*** | A comment for workers explaining how to solve the captcha correctly |
| imgInstructions | *String* | **Yes\*** | Instruction image for workers. Base64-encoded. Maximum size: 100 kB |
| minClicks       | *Number* | No       | Minimum number of tiles that must be selected. Default: `1`. Cannot exceed `rows * columns` |
| maxClicks       | *Number* | No       | Maximum number of tiles that can be selected. Default: `rows * columns` |
| canNoAnswer     | *Number* | No       | 0 — not allowed<br>1 — it is possible that no tiles match the instruction. Workers will see a "No matching images" button, and the response will return `No_matching_images` |
| previousId      | *String* | No       | ID of your previous request for the same FunCaptcha task |
| imgType         | *String* | No       | Used for accelerated recognition via Computer Vision. Supported values:<br>`funcaptcha` — FunCaptcha with tile clicking. [Learn more](https://2captcha.com/blog/funcaptcha-bypass-2-ways-solutions).<br>`recaptcha` — reCAPTCHA. [Learn more](https://2captcha.com/blog/recaptcha-recognition-using-grid-method).<br>**Important:** when using `imgType`, you must provide the `comment` in English and upload original image files (not screenshots). |

- You must provide either `comment` or `imgInstructions`.


### Request Example (FunCaptcha)

Method: [createTask](/api-docs/create-task)  
API endpoint: `https://api.2captcha.com/createTask`

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "GridTask",
        "body": "/9j/4AAQSkZJRgABAQAAAQ..HIAAAAAAQwAABtbnRyUkdCIFhZ.wc5GOGSRF//Z",
        "comment": "select all vehicles",
        "rows": 4,
        "columns": 4,
        "imgType": "funcaptcha"
    }
}
```

## Code Examples
<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
    // https://github.com/2captcha/2captcha-php

    require(__DIR__ . '/../src/autoloader.php');

    $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

    try {
        $result = $solver->grid('path/to/captcha.jpg', ['imgType' => 'funcaptcha']);
    } catch (\Exception $e) {
        die($e->getMessage());
    }

    die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
# https://github.com/2captcha/2captcha-python

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

solver = TwoCaptcha(api_key)

try:
    result = solver.grid('path/to/captcha.jpg', imgType='funcaptcha')

except Exception as e:
    sys.exit(e)

else:
    sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
    // https://github.com/2captcha/2captcha-csharp

    using System;
    using System.Linq;
    using TwoCaptcha.Captcha;

    namespace TwoCaptcha.Examples
    {
        public class GridExample
        {
            public static void Main()
            {
                var solver = new TwoCaptcha("YOUR_API_KEY");
                Grid captcha = new Grid("path/to/captcha.jpg");
                captcha.ImgType = "funcaptcha"; 
                try
                {
                    solver.Solve(captcha).Wait();
                    Console.WriteLine("Captcha solved: " + captcha.Code);
                }
                catch (AggregateException e)
                {
                    Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
                }
            }
        }
    }
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
    // https://github.com/2captcha/2captcha-java

    package examples;

    import com.twocaptcha.TwoCaptcha;
    import com.twocaptcha.captcha.Grid;

    public class GridExample {
        public static void main(String[] args) {
            TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
            Grid captcha = new Grid("path/to/captcha.jpg");
            captcha.setImgType("funcaptcha");
            try {
                solver.solve(captcha);
                System.out.println("Captcha solved: " + captcha.getCode());
            } catch (Exception e) {
                System.out.println("Error occurred: " + e.getMessage());
            }
        }

    }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
    // https://github.com/2captcha/2captcha-go

    package main

    import (
        "fmt"
        "log"
        "github.com/2captcha/2captcha-go"
    )

    func main() {
        client := api2captcha.NewClient("API_KEY")
        captcha := api2captcha.Grid{
            File: "/path/to/captcha.jpg",
            ImgType: "funcaptcha",
        }

        code, err := client.Solve(captcha.ToRequest())
        if err != nil {
            log.Fatal(err);
        }
        fmt.Println("code "+code)
    }
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
    require 'api_2captcha'

    client =  Api2Captcha.new("YOUR_API_KEY")

    result = client.grid({
      image: 'path/to/captcha.jpg',
      imgType: 'funcaptcha'
    })
  ```
  </div>
</div>

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/geetest.svg" width="320" height="160" alt="GeeTest" />

<h1>GeeTest captcha</h1>

</div>

Token-based method to bypass GeeTest.

## Task types

- **GeeTestTaskProxyless** - we use our own pool of proxies
- **GeeTestTask** - we use your proxies

## GeeTestTaskProxyless task type specification

| Property                  | Type      | Required | Description                                                                                                                                                                                                                       |
| ------------------------- | --------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **type**                  | _String_  | **Yes**  | Task type: <br>**GeeTestTaskProxyless** <br> **GeeTestTask**                                                                                                                                                                      |
| **websiteURL**            | _String_  | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users                                                                               |
| **gt**                    | _String_  | **Yes**  | GeeTest `gt` value.                                                                                                                                                                                                               |
| **challenge**             | _String_  | **Yes**  | GeeTest `challenge` value.                                                                                                                                                                                                        |
| geetestApiServerSubdomain | _String_  | No       | **Only for GeeTest v3**. Custom GeeTest API domain, for example: `api-na.geetest.com`. Can be defined inside `initGeetest` call. Also you can check the domain used to load the scripts, the default domain is `api.geetest.com`. |
| userAgent                 | _String_  | No       | User-Agent of your browser will be used to load the captcha. Use only modern browser's User-Agents                                                                                                                                |
| **version**               | _Integer_ | Yes\*    | **Should be set to `4` for GeeTest v4. Default: `3`**. GeeTest version: 3 or 4                                                                                                                                                    |
| **initParameters**        | Object    | Yes\*    | **Required for GeeTest v4**. Captcha parameters passed to `initGeetest4` call, must contain `captcha_id` value, for example: `{"captcha_id" : "e392e1d7fd421dc63325744d5a2b9c73"}`                                                |
| **risk_type**             | _String_  | No       | The `risk_type` parameter value is included in the captcha loading request. It’s dynamic, valid for a single use, and has an expiration time.                                                                                     |

> Important: you should get a new `challenge` value for each request to our API. Once captcha was loaded on the page the `challenge` value becomes invalid. You should inspect requests made to the website when page is loaded to identify a request that gets a new `challenge` value. Then you should make such request each time to get a valid `challenge` value.

## GeeTestTask task type specification

`GeeTestTask` extends `GeeTestTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | _String_  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | _String_  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | _Integer_ | **Yes**  | Proxy port                                               |
| proxyLogin       | _String_  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | _String_  | No       | Password for basic authentication on the proxy           |

## Request examples for GeeTest v3

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### GeeTestTaskProxyless request example

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "GeeTestTaskProxyless",
    "websiteURL": "https://2captcha.com/demo/geetest",
    "gt": "81388ea1fc187e0c335c0a8907ff2625",
    "challenge": "2e2f0f65240058b683cb6ea21c303eea6n"
  }
}
```

### GeeTestTask request example

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "GeeTestTask",
    "websiteURL": "https://2captcha.com/demo/geetest",
    "gt": "81388ea1fc187e0c335c0a8907ff2625",
    "challenge": "2e2f0f65240058b683cb6ea21c303eea6n",
    "proxyType": "http",
    "proxyAddress": "1.2.3.4",
    "proxyPort": "8080",
    "proxyLogin": "user23",
    "proxyPassword": "p4$w0rd"
  }
}
```

### Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
  "errorId": 0,
  "status": "ready",
  "solution": {
    "challenge": "cd8939e104fe2edb6448c8b0dc72fec6la",
    "validate": "d7b8b93452951ab2e40b40616131622f",
    "seccode": "d7b8b93452951ab2e40b40616131622f|jordan"
  },
  "cost": "0.00299",
  "ip": "1.2.3.4",
  "createTime": 1694023013,
  "endTime": 1694023041,
  "solveCount": 0
}
```

## Request examples for GeeTest v4

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### GeeTestTaskProxyless request example

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "GeeTestTaskProxyless",
    "websiteURL": "https://2captcha.com/demo/geetest-v4",
    "version": 4,
    "initParameters": {
      "captcha_id": "e392e1d7fd421dc63325744d5a2b9c73"
    }
  }
}
```

### GeeTestTask request example

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "GeeTestTask",
    "websiteURL": "https://2captcha.com/demo/geetest-v4",
    "version": 4,
    "initParameters": {
      "captcha_id": "e392e1d7fd421dc63325744d5a2b9c73"
    },
    "proxyType": "http",
    "proxyAddress": "1.2.3.4",
    "proxyPort": "8080",
    "proxyLogin": "user23",
    "proxyPassword": "p4$w0rd"
  }
}
```

### Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
  "errorId": 0,
  "status": "ready",
  "solution": {
    "captcha_id": "e392e1d7fd421dc63325744d5a2b9c73",
    "lot_number": "e6c3bed2854f41f880662c48afff5dcb",
    "pass_token": "fad5eb52fc83bf7617402fcccfb211a21e0aa1d1044",
    "gen_time": "1693924478",
    "captcha_output": "fN36ufW6cQN4SQ-JRDQC70nSq9UcQBg=="
  },
  "cost": "0.00299",
  "ip": "1.2.3.4",
  "createTime": 1692863536,
  "endTime": 1692863556,
  "solveCount": 1
}
```

## Code examples

### GeeTest v3

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

```php
// https://github.com/2captcha/2captcha-php

require(__DIR__ . '/../src/autoloader.php');

$solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

try {
  $result = $solver->geetest([
      'gt'        => '81388ea1fc187e0c335c0a8907ff2625',
      'apiServer' => 'api.geetest.com',
      'challenge' => '12345678abc90123d45678ef90123a456b',
      'url'       => 'https://2captcha.com/demo/geetest',
  ]);
} catch (\Exception $e) {
  die($e->getMessage());
}

die('Captcha solved: ' . $result->code);
```

  </div>

  <div id="python-code-example" data-component="TabPanel">

```python
# https://github.com/2captcha/2captcha-python

import sys
import os
import requests
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

solver = TwoCaptcha(api_key)

resp = requests.get("https://2captcha.com/api/v1/captcha-demo/gee-test/init-params")
data = json.loads(resp)
challenge = data["challenge"]

try:
  result = solver.geetest(gt='f3bf6dbdcf7886856696502e1d55e00c',
                          apiServer='api.geetest.com',
                          challenge=challenge,
                          url='https://2captcha.com/demo/geetest')

except Exception as e:
  sys.exit(e)

else:
  sys.exit('solved: ' + str(result))
```

  </div>

  <div id="csharp-code-example" data-component="TabPanel">

```csharp
// https://github.com/2captcha/2captcha-csharp

using System;
using System.Linq;
using TwoCaptcha.Captcha;

namespace TwoCaptcha.Examples
{
  public class GeeTestExample
  {
      public void Main()
      {
          TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
          GeeTest captcha = new GeeTest();
          captcha.SetGt("81388ea1fc187e0c335c0a8907ff2625");
          captcha.SetApiServer("api.geetest.com");
          captcha.SetChallenge("12345678abc90123d45678ef90123a456b");
          captcha.SetUrl("https://2captcha.com/demo/geetest");
          try
          {
              solver.Solve(captcha).Wait();
              Console.WriteLine("Captcha solved: " + captcha.Code);
          }
          catch (AggregateException e)
          {
              Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
          }
      }
  }
}
```

  </div>

  <div id="java-code-example" data-component="TabPanel">

```java
// https://github.com/2captcha/2captcha-java

package examples;

import com.twocaptcha.TwoCaptcha;
import com.twocaptcha.captcha.GeeTest;

public class GeeTestExample {
  public static void main(String[] args) {
      TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
      GeeTest captcha = new GeeTest();
      captcha.setGt("81388ea1fc187e0c335c0a8907ff2625");
      captcha.setApiServer("api.geetest.com");
      captcha.setChallenge("12345678abc90123d45678ef90123a456b");
      captcha.setUrl("https://2captcha.com/demo/geetest");
      try {
          solver.solve(captcha);
          System.out.println("Captcha solved: " + captcha.getCode());
      } catch (Exception e) {
          System.out.println("Error occurred: " + e.getMessage());
      }
  }

}
```

  </div>

  <div id="go-code-example" data-component="TabPanel">

```go
// https://github.com/2captcha/2captcha-go

package main

import (
  "fmt"
  "log"
  "github.com/2captcha/2captcha-go"
)

func main() {
  client := api2captcha.NewClient("API_KEY")
  captcha := api2captcha.GeeTest{
      GT: "81388ea1fc187e0c335c0a8907ff2625",
      ApiServer: "api.geetest.com",
      Challenge: "12345678abc90123d45678ef90123a456b",
      Url: "https://2captcha.com/demo/geetest",
  }
  code, err := client.Solve(captcha.ToRequest())
  if err != nil {
      log.Fatal(err);
  }
  fmt.Println("code "+code)
}
```

  </div>

  <div id="ruby-code-example" data-component="TabPanel">

```ruby
require 'api_2captcha'

client =  Api2Captcha.new("YOUR_API_KEY")

result = client.geetest({
gt: '81388ea1fc187e0c335c0a8907ff2625',
api_server: 'api-na.geetest.com',
challenge: '12345678abc90123d45678ef90123a456b',
pageurl: 'https://2captcha.com/demo/geetest'
})
```

  </div>
</div>

### GeeTest v4

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

```php
$result = $solver->geetest_v4([
  'captchaId' => 'e392e1d7fd421dc63325744d5a2b9c73',
  'challenge' => 'd1a9ddd7-e36f-4100-be9f-231f11743656',
  'url'       => 'https://2captcha.com/demo/geetest-v4',
]);
```

  </div>

  <div id="python-code-example" data-component="TabPanel">

```python
result = solver.geetest_v4(captcha_id='e392e1d7fd421dc63325744d5a2b9c73',
                      url='https://2captcha.com/demo/geetest-v4',
                      challenge="d1a9ddd7-e36f-4100-be9f-231f11743656")
```

  </div>

  <div id="csharp-code-example" data-component="TabPanel">

```csharp
GeeTestV4 captcha = new GeeTestV4();
captcha.SetCaptchaId("e392e1d7fd421dc63325744d5a2b9c73");
captcha.SetUrl("https://2captcha.com/demo/geetest-v4");
```

  </div>

  <div id="java-code-example" data-component="TabPanel">

```java
GeeTestV4 captcha = new GeeTestV4();
captcha.setCaptchaId("e392e1d7fd421dc63325744d5a2b9c73");
captcha.setUrl("https://2captcha.com/demo/geetest-v4");
```

  </div>

  <div id="go-code-example" data-component="TabPanel">

```go

```

  </div>

  <div id="ruby-code-example" data-component="TabPanel">

```ruby
require 'api_2captcha'

  client =  Api2Captcha.new("YOUR_API_KEY")

  result = client.geetest_v4({
      captcha_id: 'e392e1d7fd421dc63325744d5a2b9c73',
      pageurl: 'https://2captcha.com/demo/geetest-v4"'
  })
```

  </div>
</div>

## Useful links

- [GeeTest v3 demo page](/demo/geetest)
- [GeeTest v4 demo page](/demo/geetest-v4)
- [How to bypass GeeTest](/p/geetest)
- [Video how to bypass GeeTest](https://youtu.be/oUKBX0lleUY)

---

# getBalance method

Returns your account balance

**API Endpoint:** `https://api.2captcha.com/getBalance`
**Method:** `POST`
**Content-Type:** `application/json`

## Request properties

| Name          | Type     | Required | Description                |
| ------------- | -------- | -------- | -------------------------- |
| **clientKey** | *String* | **Yes**  | Your [API key](/enterpage) |


## Request example

```json
{
   "clientKey": "YOUR_API_KEY"
}
```

## Response example

```json
{
    "errorId": 0,
    "balance": 0.93958
}
```

---

# getTaskResult method

Returns the result for a task.
The result format depends on task type and described in the task specification.

**API Endpoint:** `https://api.2captcha.com/getTaskResult`
**Method:** `POST`
**Content-Type:** `application/json`

## Request properties

| Name          | Type      | Required | Description                |
| ------------- | --------- | -------- | -------------------------- |
| **clientKey** | *String*  | **Yes**  | Your [API key](/enterpage) |
| **taskId**    | *Integet* | **Yes**  | The id of your task        |

## Request example 

```json
{
   "clientKey": "YOUR_API_KEY", 
   "taskId": 74372499131
}
```


## Response examples

### In progress

When the task is not complete yet, you receive the following response. Wait at least 5 seconds and repeat the request.

```json
{
    "errorId": 0,
    "status": "processing"
}
```


### Task could not be completed

If workers were unable to complete the task you get the response containing the [error id](/api-docs/error-codes).

```json
{
    "errorId": 12,
    "errorCode": "ERROR_CAPTCHA_UNSOLVABLE",
    "errorDescription": "Workers could not solve the Captcha"
}
```

### Task completed

When the task is completed you receive the solution according to the task type format and some common task data like the timestamps, price, IP that submitted the request.

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {},
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

#### Response specification

| Property   | Type      | Description |
| ---------- | --------- | ----------- |
| errorId    | *Integer* | The [error id](/api-docs/error-codes) for cases when the task can not be completed  |
| status     | *String*  | **ready** - the task is completed successfully <br>**processing** - we are still processing your task, please repeat the request again in 5-10 seconds |
| solution   | *Object*  | An object contaning the solution for your task. The format of the object can be found in task type specification |
| cost       | *String*  | The task price charged from your balance |
| ip         | *String*  | The IP address submitted the task request |
| createTime | *Integer* | Timestamp indicating the moment task was submitted | 
| endTime    | *Integer* | Timestamp indicating the moment task was completed | 
| solveCount | *Integer* | The number of workers attempted to complete your task |

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/grid.svg" width="320" height="160" alt="Grid" />

<h1>Grid Method</h1>

</div>

The method can be used to bypass tasks where a grid is applied to an image and you need to click on grid tiles, like reCAPTCHA images.


Returns the array of tile indexes, where 1 is top left tile.

**Supported image formats:** JPEG, PNG, GIF
**Max file size:** 600 kB
**Max image size:** 1000px on any side

## GridTask task type specification

| Property        | Type      | Required| Description  |
| --------------- | --------- | ------- | ------------ |
| **type**        | *String*  | **Yes** | **GridTask** |
| **body**        | *String*  | **Yes** | Image encoded into Base64 format. Data-URI format (containing `data:content/type` prefix) is also supported |
| rows            | *Integer* | No      | Number of grid rows |
| columns         | *Integer* | No      | Number of grid columns |
| comment         | *String*  |**Yes\***| A comment will be shown to workers to help them to solve the captcha properly |
| imgInstructions | *String*  |**Yes\***| An image with instruction that will be shown to workers. Image should be encoded into Base64 format. Max file size: 100 kB |
| previousId      | *String* | No      | Id of your previous request with the same captcha challenge |
| imgType         | *String* | No      | The image will be recognized using Computer Vision, which significantly reduces the time needed to solve the captcha. Supported value options: <br> `funcaptcha` - sending FunCaptcha, the version in which you need to click on the square matching the requirements.  [More info here](https://2captcha.com/blog/funcaptcha-bypass-2-ways-solutions).<br>`recaptcha` - sending reCAPTCHA. [More info here](https://2captcha.com/blog/recaptcha-recognition-using-grid-method).<br> <b>Important:</b> when using the `imgType` parameter, it is required to send the `comment` parameter containing the original instructions for the captcha in English, and you also need to send the original image files and not screenshots.|
| previousId      | *String*  | No      | Id of your previous request with the same captcha challenge |
| minClicks       | *Integer* | No      | The minimum number of tiles that must be selected. Default: `1`. Can't  be more than `rows * columns` |
| maxClicks       | *Integer* | No      | The maximum number of tiles that can be selected on the image. Default: `rows * columns` |
| canNoAnswer     | *Integer* | No      | 0 - not specified<br>1 - possibly there's no images that fit the instruction.<br>Set the value to 1 only if it's possible that there's no images matching to the instruction. We'll provide a button "No matching images" to worker and you will receive *No_matching_images* as answer. |

 - you should provide at least one of the properties: `comment` or `imgInstructions`

### Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"GridTask",
        "body":"/9j/4AAQSkZJRgABAQAAAQ..HIAAAAAAQwAABtbnRyUkdCIFhZ.wc5GOGSRF//Z",
        "comment":"select all vehicles",
        "rows": 4,
        "columns": 4
    }
}
```

### Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "click": [
            4,
            8,
            12,
            16
        ]
    },
    "cost": "0.0012",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
    // https://github.com/2captcha/2captcha-php

    require(__DIR__ . '/../src/autoloader.php');

    $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

    try {
        $result = $solver->grid('path/to/captcha.jpg');
    } catch (\Exception $e) {
        die($e->getMessage());
    }

    die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
# https://github.com/2captcha/2captcha-python

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

solver = TwoCaptcha(api_key)

try:
    result = solver.grid('path/to/captcha.jpg')

except Exception as e:
    sys.exit(e)

else:
    sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
    // https://github.com/2captcha/2captcha-csharp

    using System;
    using System.Linq;
    using TwoCaptcha.Captcha;

    namespace TwoCaptcha.Examples
    {
        public class GridExample
        {
            public static void Main()
            {
                var solver = new TwoCaptcha("YOUR_API_KEY");
                Grid captcha = new Grid("path/to/captcha.jpg");
                try
                {
                    solver.Solve(captcha).Wait();
                    Console.WriteLine("Captcha solved: " + captcha.Code);
                }
                catch (AggregateException e)
                {
                    Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
                }
            }
        }
    }
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
    // https://github.com/2captcha/2captcha-java

    package examples;

    import com.twocaptcha.TwoCaptcha;
    import com.twocaptcha.captcha.Grid;

    public class GridExample {
        public static void main(String[] args) {
            TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
            Grid captcha = new Grid("path/to/captcha.jpg");
            try {
                solver.solve(captcha);
                System.out.println("Captcha solved: " + captcha.getCode());
            } catch (Exception e) {
                System.out.println("Error occurred: " + e.getMessage());
            }
        }

    }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
    // https://github.com/2captcha/2captcha-go

    package main

    import (
        "fmt"
        "log"
        "github.com/2captcha/2captcha-go"
    )

    func main() {
        client := api2captcha.NewClient("API_KEY")
        captcha := api2captcha.Grid{
            File: "/path/to/captcha.jpg",
        }
        code, err := client.Solve(captcha.ToRequest())
        if err != nil {
            log.Fatal(err);
        }
        fmt.Println("code "+code)
    }
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
    require 'api_2captcha'

    client =  Api2Captcha.new("YOUR_API_KEY")

    result = client.grid({ image: 'path/to/captcha.jpg'})
    # OR
    result = client.grid({
    image: 'https://site-with-captcha.com/path/to/captcha.jpg'
    })
  ```
  </div>
</div>

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/hunt-captcha.svg" width="320" height="160" alt="Hunt" />

<h1>Hunt captcha</h1>

</div>

A token-based method for bypassing Hunt captcha.

There are two modes: without `data`, the task returns X-HD. With `data`, the task solves the captcha using a `meta.token` you already received from the site. X-HD is a unique fingerprint tied to your IP that you can use for subsequent requests to the site.


**Typical workflow:**

1. Create a task without `data`.
2. Get X-HD.
3. Send a request to the site with this X-HD.
4. Receive `meta.token` from the site.
5. Create a new task with `data = meta.token`.
6. Get the solution.
7. Submit the solution to the site.

## Task types
- **HuntTask** — we use the proxy you provide

## Specification for HuntTask

| Property                | Type      | Required | Description  |
| ----------------------- | -------- | ---------- | --------- |
| **type**                | *String* | **Yes**     | Task type: <br>**HuntTask** |
| **websiteURL**          | *String* | **Yes**     | Full URL of the target web page where the captcha loads |
| **apiGetLib**          | *String* | **Yes**     | Full link to the api.js file. |
| userAgent               | *String* | No        | Browser User-Agent used to open the page |
| data             | *String* | No        | Value of `meta.token` that the site returned after a request with X-HD. Use only for the captcha solving mode |
| **proxyType**    | *String*  | **Yes**     | Proxy type: <br>**http** <br> **socks4** <br> **socks5**  |
| **proxyAddress** | *String*  | **Yes**     | Proxy server IP address or hostname                     |
| **proxyPort**    | *Number*   | **Yes**     | Proxy server port                                       |
| proxyLogin       | *String*  | No        | Login for proxy authentication                |
| proxyPassword    | *String*  | No        | Password for proxy authentication               |

## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### Example HuntTask request with `data` 

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
      "type": "HuntTask",
      "websiteURL": "https://example.com/page-with-hunt",
      "apiGetLib": "https://example.com/hd-api/external/apps/app-id/api.js",
      "data": "kufyHK/s/j...wIW",
      "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
      "proxyType": "http",
      "proxyAddress": "1.2.3.4",
      "proxyPort": 8080,
      "proxyLogin": "login",
      "proxyPassword": "password"
    }
  }
```


## Example response

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "6IyDCCpDd.../z/kLNSpjewI="
        },
    "cost": "0.003",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```
## How to work with cookies correctly

The site uses cookies to track your `session`. If you don't send them with your requests, the server will simply reject the request or ask you to verify again.

**Example cookie string the site returns:**
`platform_type=desktop; typeBetNames=full; _glhf=1234567890; coefview=0; visit=1-123abc012345d1be726746568edc62d9; fast_coupon=true;
v3fr=1; lng=en; flaglng=en; SESSION=12a3aea8cdcfdbb9e7df8ee99b526a84; auid=ab0dW2mqlz1Tjo2AAwplAg==; ggru=195; che_g=12abcede-691f-c7b2-d1e8-8488bc557d98`

### Main steps for working with cookies:

1. First, open the target page or send a regular `GET` request. The server will create a session and send initial `cookies`.
2. Look for `cookies` in the `Set-Cookie` response header. This usually contains the session ID, security parameters, and bot protection data.
3. Save the values you receive. You will need them for all subsequent requests.
4. When sending requests to the API, add the saved `cookies` to the `Cookie` header. This way the server knows the requests come from the same session.
5. Send all requests from the same IP address or proxy and with the same `User-Agent` header. If you change these values, the security system may flag the activity and require re-verification.
6. Some `cookies` are created by the site itself via JavaScript. When automating, the easiest approach is to take ready-made `cookies` from a working browser or generate them using the same logic.

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/imperva-captcha.svg" width="320" height="160" alt="imperva" />

<h1>Imperva (Incapsula)</h1>

</div>

A cookie-based method for bypassing the Imperva (Incapsula) captcha.

> **IMPORTANT**: some parameters are generated dynamically and may differ with each load of a page protected by Imperva (Incapsula).

## Task types

- **IncapsulaTask**: we use the proxy you provide

## IncapsulaTask specification

| Property             | Type      | Required | Description |
|----------------------|-----------|----------|-------------|
| **type**             | *String*  | **Yes**  | Task type:<br>**IncapsulaTask** |
| **websiteURL**       | *String*  | **Yes**  | The full URL of the target web page where the captcha is loaded |
| **incapsulaScriptUrl** | *String*| **Yes**  | `_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3`: the name of the Incapsula JS file |
| **incapsulaCookies** | *String*  | **Yes**  | Your Incapsula cookies. You can get them on the page via `document.cookie` or from the `Set-Cookie: "incap_sess_*=...; visid_incap_*=..."` header |
| userAgent            | *String*  | No       | The browser User-Agent used to open the page |
| reese84UrlEndpoint   | *String*  | No       | The endpoint name where the Reese84 fingerprint is sent. You can find it among the requests, it ends with `?d=site.com` |
| **proxyType**        | *String*  | **Yes**  | Proxy type:<br>**http**<br>**socks4**<br>**socks5** |
| **proxyAddress**     | *String*  | **Yes**  | The IP address or hostname of the proxy server |
| **proxyPort**        | *Number*  | **Yes**  | The proxy server port |
| proxyLogin           | *String*  | No       | Login for proxy server authentication |
| proxyPassword        | *String*  | No       | Password for proxy server authentication |

## Request examples

Method: [createTask](/api-docs/create-task)

API endpoint: `https://api.2captcha.com/createTask`

### IncapsulaTask request example

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "ImpervaTask",
    "websiteUrl": "https://site-example.com/login",
    "incapsulaScriptUrl": "_Incapsula_Resource?SWJIYLWA=abc123def456ghi789jkl012mno345pq",
    "incapsulaCookies": "incap_ses_1234_567890=abcDEF123ghiJKL456mnoPQR789stuVWXYZ==; visid_incap_567890=xyzABC123defGHI456jklMNOpqr789STUVWXYZ;",
    "reese84UrlEndpoint": "https://site-example.com/_Incapsula_Resource?reese84=1",
    "userAgent": "Mozilla/5.0 (Windows NT AA.B; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "proxyType": "http",
    "proxyAddress": "1.2.3.4",
    "proxyPort": 8080,
    "proxyLogin": "login",
    "proxyPassword": "password"
  }
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
  "errorId": 0,
  "status": "ready",
  "solution": {
    "domains": {
      "https://site-example.com": {
        "cookies": {
          "___utmvc": "abc123XYZ789def456GHI012...jkl345MNO678pqr901STU234==; Max-Age=31536000; Domain=.domain-example.com; Path=/; Secure; SameSite=Lax"
        }
      }
    }
  }
}
```

The cookies from `solution.domains` must be passed to the target site. If the response includes `solution.headers.User-Agent`, use the same User-Agent in the request to the site.

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/keycaptcha.svg" width="320" height="160" alt="KeyCAPTCHA widget" />

<h1>KeyCAPTCHA</h1>

</div>

Token-based method to bypass KeyCAPTCHA.


## Task types
- **KeyCaptchaTaskProxyless** - we use our own pool of proxies
- **KeyCaptchaTask** - we use your proxies

## KeyCaptchaTaskProxyless task type specification

| Property                  | Type     | Required | Description |
| ------------------------- | -------- | -------- | ----------- |
| **type**                  | *String* | **Yes**  | Task type: <br>**KeyCaptchaTaskProxyless** <br>  **KeyCaptchaTask** |
| **websiteURL**            | *String* | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **s_s_c_user_id**         | *String* | **Yes**  | The value of `s_s_c_user_id` parameter found on page |
| **s_s_c_session_id**      | *String* | **Yes**  | The value of `s_s_c_session_id` parameter found on page |
| **s_s_c_web_server_sign** | *String* | **Yes**  | The value of `s_s_c_web_server_sign` parameter found on page |
| **s_s_c_web_server_sign2**| *String* | **Yes**  | The value of `s_s_c_web_server_sign2` parameter found on page |


## KeyCaptchaTask task type specification

`KeyCaptchaTask` extends `KeyCaptchaTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### KeyCaptchaTaskProxyless

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "KeyCaptchaTaskProxyless",
    "s_s_c_user_id": 10,
    "s_s_c_session_id": "493e52c37c10c2bcdf4a00cbc9ccd1e8",
    "s_s_c_web_server_sign": "9006dc725760858e4c0715b835472f22-pz-",
    "s_s_c_web_server_sign2": "2ca3abe86d90c6142d5571db98af6714",
    "websiteURL": "https://2captcha.com/demo/keycaptcha"
  }
}
```


### KeyCaptchaTask

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "KeyCaptchaTask",
        "s_s_c_user_id": 184015,
        "s_s_c_session_id": "80f5f77b8b396b6cb6ea59cf22c38c55",
        "s_s_c_web_server_sign": "418910f3da05d4e3125030e4f9c95d42",
        "s_s_c_web_server_sign2": "118b538926cf9aafc48926bcaccf4c0e",
        "websiteURL": "https://2captcha.com/demo/keycaptcha",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": "8080",
        "proxyLogin": "user23",
        "proxyPassword": "p4$w0rd"
    }
}
```


## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "84f42ee334f6bd760b8be3b2b...492598266d7a2418511776505f79|1"
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 0
}
```

## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
  // https://github.com/2captcha/2captcha-php

  require(__DIR__ . '/../src/autoloader.php');

  $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

  try {
      $result = $solver->keycaptcha([
          's_s_c_user_id'          => 184015,
          's_s_c_session_id'       => '9ff29e0176e78eb7ba59314f92dbac1b',
          's_s_c_web_server_sign'  => '964635241a3e5e76980f2572e5f63452',
          's_s_c_web_server_sign2' => '3ca802a38ffc5831fa293ac2819b1204',
          'url'                    => 'https://2captcha.com/demo/keycaptcha',
      ]);
  } catch (\Exception $e) {
      die($e->getMessage());
  }

  die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
  # https://github.com/2captcha/2captcha-python

  import sys
  import os

  sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

  from twocaptcha import TwoCaptcha

  api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

  solver = TwoCaptcha(api_key)

  try:
      result = solver.keycaptcha(
          s_s_c_user_id=184015,
          s_s_c_session_id='9ff29e0176e78eb7ba59314f92dbac1b',
          s_s_c_web_server_sign='964635241a3e5e76980f2572e5f63452',
          s_s_c_web_server_sign2='3ca802a38ffc5831fa293ac2819b1204',
          url='https://2captcha.com/demo/keycaptcha')

  except Exception as e:
      sys.exit(e)

  else:
      sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
  // https://github.com/2captcha/2captcha-csharp

  using System;
  using System.Linq;
  using TwoCaptcha.Captcha;

  namespace TwoCaptcha.Examples
  {
      public class KeyCaptchaExample
      {
          public void Main()
          {
              TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
              KeyCaptcha captcha = new KeyCaptcha();
              captcha.SetUserId(184015);
              captcha.SetSessionId("9ff29e0176e78eb7ba59314f92dbac1b");
              captcha.SetWebServerSign("964635241a3e5e76980f2572e5f63452");
              captcha.SetWebServerSign2("3ca802a38ffc5831fa293ac2819b1204");
              captcha.SetUrl("https://2captcha.com/demo/keycaptcha");
              try
              {
                  solver.Solve(captcha).Wait();
                  Console.WriteLine("Captcha solved: " + captcha.Code);
              }
              catch (AggregateException e)
              {
                  Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
              }
          }
      }
  }
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
  // https://github.com/2captcha/2captcha-java

  package examples;

  import com.twocaptcha.TwoCaptcha;
  import com.twocaptcha.captcha.KeyCaptcha;

  public class KeyCaptchaExample {
      public static void main(String[] args) {
          TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
          KeyCaptcha captcha = new KeyCaptcha();
          captcha.setUserId(184015);
          captcha.setSessionId("9ff29e0176e78eb7ba59314f92dbac1b");
          captcha.setWebServerSign("964635241a3e5e76980f2572e5f63452");
          captcha.setWebServerSign2("3ca802a38ffc5831fa293ac2819b1204");
          captcha.setUrl("https://2captcha.com/demo/keycaptcha");
          try {
              solver.solve(captcha);
              System.out.println("Captcha solved: " + captcha.getCode());
          } catch (Exception e) {
              System.out.println("Error occurred: " + e.getMessage());
          }
      }
  }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
  // https://github.com/2captcha/2captcha-go

  package main

  import (
      "fmt"
      "log"
      "github.com/2captcha/2captcha-go"
  )

  func main() {
      client := api2captcha.NewClient("API_KEY")
      captcha := api2captcha.KeyCaptcha{
          UserId: 184015,
          SessionId: "9ff29e0176e78eb7ba59314f92dbac1b",
          WebServerSign: "964635241a3e5e76980f2572e5f63452",
          WebServerSign2: "3ca802a38ffc5831fa293ac2819b1204",
          Url: "https://2captcha.com/demo/keycaptcha",   
      }
      code, err := client.Solve(captcha.ToRequest())
      if err != nil {
          log.Fatal(err);
      }
      fmt.Println("code "+code)
  }
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
  # https://github.com/2captcha/2captcha-ruby
  require 'api_2captcha'

  client =  Api2Captcha.new("YOUR_API_KEY")

  result = client.keycaptcha({
    s_s_c_user_id: 184015,
    s_s_c_session_id: '9ff29e0176e78eb7ba59314f92dbac1b',
    s_s_c_web_server_sign: '964635241a3e5e76980f2572e5f63452-pz-',
    s_s_c_web_server_sign2: '3ca802a38ffc5831fa293ac2819b1204',
    pageurl: 'https://2captcha.com/demo/keycaptcha'
  })
  ```
  </div>
</div>



## Useful links
- [KeyCaptcha demo page](/demo/keycaptcha)

---

# Language support

Our API allows you to set the language of captcha with `languagePool` parameter.

Each our worker can tell us which languages he speaks. When you submit a captcha with `languagePool` parameter we will distribute your captcha to workers who speak the language. That allows you to solve non-latin and non-cyrillic captchas, for example chinese or vietnamese.

The list of supported languages is available in the table below.

| **Language code (`languagePool` value)** | **Language** |
| --- | --- |
| en | English |
| ru | Russian |
| es | Spanish |
| pt | Portuguese |
| uk | Ukrainian |
| vi | Vietnamese |
| fr | French |
| id | Indonesian |
| ar | Arab |
| ja | Japanese |
| tr | Turkish |
| de | German |
| zh | Chinese |
| fil | Philippine |
| pl | Polish |
| th | Thai |
| it | Italian |
| nl | Nederlands (Dutch) |
| sk | Slovak |
| bg | Bulgarian |
| ro | Romanian |
| hu | Hungarian (Magyar) |
| ko | Korean |
| cs | Czech |
| az | Azerbaijani |
| fa | Persian (Farsi) |
| bn | Bengali |
| el | Greek |
| lt | Lithuanian |
| lv | Latvian |
| sv | Swedish |
| sr | Serbian |
| hr | Croatian |
| he | Hebrew |
| hi | Hindi |
| nb | Norwegian |
| sl | Slovenian |
| da | Danish |
| uz | Uzbek |
| fi | Finnish |
| ca | Catalan |
| ka | Georgian |
| ms | Malay |
| te | Telugu |
| et | Estonian |
| ml | Malayalam |
| be | Belorussian |
| kk | Kazakh |
| mr | Marathi |
| ne | Nepali |
| my | Burmese |
| bs | Bosnian |
| hy | Armenian |
| mk | Macedonian |
| pa | Punjabi |

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/lemin.svg" width="320" height="160" alt="Lemin widget" />

<h1>Lemin captcha</h1>

</div>

Token-based method to bypass Lemin Puzzle captcha.


## Task types
- **LeminTaskProxyless** - we use our own pool of proxies
- **LeminTask** - we use your proxies

## LeminTaskProxyless task type specification

| Property                | Type     | Required | Description |
| ----------------------- | -------- | -------- | ----------- |
| **type**                | *String* | **Yes**  | Task type: <br>**LeminTaskProxyless** <br>  **LeminTask** |
| **websiteURL**          | *String* | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **captchaId**           | *String* | **Yes**  | Lemin `captchaId` value. Unique for a website. |
| **divId**               | *String* | **Yes**  | The `id` of captcha parent `div` element |
| leminApiServerSubdomain | *String* | No       | API  domain used to load the captcha scripts. Default: `https://api.leminnow.com/`|
| userAgent               | *String* | No       | User-Agent of your browser will be used to load the captcha. Use only modern browser's User-Agents|


## LeminTask task type specification

`LeminTask` extends `LeminTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### LeminTaskProxyless

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"LeminTaskProxyless",
        "captchaId":"CROPPED_3dfdd5c_d1872b526b794d83ba3b365eb15a200b",
        "divId":"lemin-cropped-captcha",
        "leminApiServerSubdomain":"api.leminnow.com",
        "websiteURL":"https://2captcha.com/demo/lemin"
    }
}
```

### LeminTask

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"LeminTask",
        "captchaId":"CROPPED_3dfdd5c_d1872b526b794d83ba3b365eb15a200b",
        "divId":"lemin-cropped-captcha",
        "leminApiServerSubdomain":"api.leminnow.com",
        "websiteURL":"https://2captcha.com/demo/lemin",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": "8080",
        "proxyLogin": "user23",
        "proxyPassword": "p4$w0rd"
    }
}
```


## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "answer": "0xaxakx0xaxaax0xkxx3ox0x3ox3ox...gAAAAABk8bgzEFOg9i3Jm",
        "challenge_id": "e0348984-92ec-23af-1488-446e3a58946c"
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```


## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
  // https://github.com/2captcha/2captcha-php
    $result = $solver->lemin([
        'captchaId' => 'CROPPED_d3d4d56_73ca4008925b4f83a8bed59c2dd0df6d',
        'apiServer' => 'api.leminnow.com',
        'url'       => 'http://sat2.aksigorta.com.tr',
    ]);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
  # https://github.com/2captcha/2captcha-python

    result = solver.lemin(captcha_id='CROPPED_1abcd2f_a1234b567c890d12ef3a456bc78d901d',
                                div_id='lemin-cropped-captcha', 
                                url='https://www.site.com/page/',
                                param1=..., ...)

  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
  // https://github.com/2captcha/2captcha-csharp

    Lemin captcha = new Lemin();
    captcha.SetCaptchaId("CROPPED_d3d4d56_73ca4008925b4f83a8bed59c2dd0df6d");
    captcha.SetApiServer("api.leminnow.com");
    captcha.SetUrl("http://sat2.aksigorta.com.tr");
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
  // https://github.com/2captcha/2captcha-java

    Lemin captcha = new Lemin();      
    captcha.setСaptchaId("CROPPED_d3d4d56_73ca4008925b4f83a8bed59c2dd0df6d");
    captcha.setUrl("http://sat2.aksigorta.com.tr");
    captcha.setApiServer("api.leminnow.com");
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
  // https://github.com/2captcha/2captcha-go

    captcha := Lemin {
        CaptchaId: "CROPPED_3dfdd5c_d1872b526b794d83ba3b365eb15a200b",
        Url:   "https://www.site.com/page/",
        DivId:     "lemin-cropped-captcha",
        ApiServer: "api.leminnow.com",
    }
    req := captcha.ToRequest()
    req.SetProxy("HTTPS", "login:password@IP_address:PORT")
    code, err := client.Solve(req)
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
  # https://github.com/2captcha/2captcha-ruby

    result = client.lemin({
    captcha_id: 'CROPPED_1abcd2f_a1234b567c890d12ef3a456bc78d901d',
    div_id: 'lemin-cropped-captcha',
    pageurl: 'https://www.site.com/page/',
    api_server: "https://api.leminnow.com/"
    })
  ```
  </div>
</div>


## Useful links

* [Demo page Lemin Cropped Captcha](/demo/lemin)
* [How to bypass Lemin Cropped Captcha](/p/lemin-captcha)
* [Video how to bypass Lemin Cropped Captcha](https://www.youtube.com/watch?v=Gfx8_Z6TZkM)

---

# Request limits

Please remember and understand that each of your requests to our API generates multuple requests to our databases. That's why we ask to set proper timeouts for your requests and use proper [error handling](/api-docs/error-codes) for cases when server returns an error (error message, HTTP error or HTML page with error).

For example:

- If server returns ERROR_NO_SLOT_AVAILABLE make a 5 seconds timeout before sending next request.
- If server returns ERROR_ZERO_BALANCE set the timeout to 60 seconds.
- After uploading a captcha wait a least 1-2 sec. and only then try to get the answer.
- If captcha is not solved yet - retry in 5 seconds.

If your timeouts are configured incorrectly your account or IP address will be temporary blocked and server will return an error. See the list of error codes in the [table](/api-docs/error-codes).

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/mtcaptcha.svg" width="320" height="160" alt="mtcaptcha widget" />

<h1>MTCaptcha</h1>

</div>

Token-based method for automated solving of MTCaptcha.


## Task types
- **MtCaptchaTaskProxyless** - we use our own proxies pool to load and solve the captcha
- **MtCaptchaTask** - we use your proxies

## Task specification

| Property                 | Type     | Required | Description                                                         |
| ------------------------ | -------- | -------- | ------------------------------------------------------------------- |
| **type**                 | *String* | **Yes**  | Task type: <br>**MtCaptchaTaskProxyless** <br>  **MtCaptchaTask**   |
| **websiteURL**           | *String* | **Yes**  | The full URL of target web page where the captcha is loaded.        |
| **websiteKey**           | *String* | **Yes**  | The MTCaptcha `sitekey` value found in the page code.               | 


## MtCaptchaTask task type specification

`MtCaptchaTask` extends `MtCaptchaTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### MtCaptchaTaskProxyless

```json
{
  "clientKey": "{{clientKey}}",
  "task": {
    "type": "MtCaptchaTaskProxyless",
    "websiteURL": "https://service.mtcaptcha.com/mtcv1/demo/index.html",
    "websiteKey": "MTPublic-DemoKey9M"
  }
}

```

### MtCaptchaTask

```json
{
  "clientKey": "{{clientKey}}",
  "task": {
    "type": "MtCaptchaTask",
    "websiteURL": "https://service.mtcaptcha.com/mtcv1/demo/index.html",
    "websiteKey": "MTPublic-DemoKey9M",
    "proxyType":"http",
    "proxyAddress":"1.2.3.4",
    "proxyPort":"8080",
    "proxyLogin":"user23",
    "proxyPassword":"p4$w0rd"
  }
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "v1(00cc43a5,1adfe4b4,MTPublic-DemoKey9M,0080ab49...IJexMsishqlg**)"
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1695129688,
    "endTime": 1695129702,
    "solveCount": 1
}

```

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/normal.svg" width="320" height="160" alt="Captcha image" />

<h1>Normal captcha</h1>

</div>

Normal captcha is an image that contains distored but human-readable text. To solve the captcha user have to type the text from the image.

## Task type: ImageToTextTask

The method is used to get the text from distorted captcha images. Images should be encoded to [Base64](https://en.wikipedia.org/wiki/Base64) format.

**Supported image formats:** JPEG, PNG, GIF
**Max file size:** 100 kB
**Max image size:** 1000px on any side


## ImageToTextTask task type specification

| Property        | Type      | Required | Default             | Description   |
| --------------- | --------- | -------- | ------------------- | ------------- |
| **type**        | *String*  | **Yes**  | **ImageToTextTask** | Task type     |
| **body**        | *String*  | **Yes**  |                     | Image encoded into Base64 format. Data-URI format (containing `data:content/type` prefix) is also supported |
| phrase          | *Boolean* | No       | false               | **false** - no preference <br> **true** - the answer should contain at least two words separated by space.   |
| case            | *Boolean* | No       | false               | **false** - no preference <br> **true** - the result is case-sensitive|  |
| numeric         | *Integer* | No       | 0                   | **0** - no preference <br> **1** - answer should contain only numbers <br> **2** - answer should contain only letters <br> **3** - answer should contain only numbers OR only letters <br> **4** - answer MUST contain both numbers AND letters |
| math            | *Boolean* | No       | false               | **false** - no preference <br> **true** - captcha requires calculation |
| minLength       | *Integer* | No       | 0                   | **0** - no preference <br> **>=1** - defines minimal answer length |
| maxLength       | *Integer* | No       | 0                   | **0** - no preference <br> **>=1** - defines maximal answer length |
| comment         | *String*  | No       |                     | A comment will be shown to workers to help them to solve the captcha properly |
| imgInstructions | *String*  | No       |                     | An optional image with instruction that will be shown to workers. Image should be encoded into Base64 format. |


## Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "ImageToTextTask",
        "body": "R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==",
        "phrase": false,
        "case": true,
        "numeric": 0,
        "math": false,
        "minLength": 1,
        "maxLength": 5,
        "comment": "enter the text you see on the image"
    },
    "languagePool": "en"
}
```


### Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "text": "hello world"
    },
    "cost": "0.00025",
    "ip": "1.2.3.4",
    "createTime": 1692808229,
    "endTime": 1692808326,
    "solveCount": 1
}
```


## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
    // https://github.com/2captcha/2captcha-php

    require(__DIR__ . '/../src/autoloader.php');

    $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

    try {
        $result = $solver->normal('path/to/captcha.jpg');
    } catch (\Exception $e) {
        die($e->getMessage());
    }

    die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
# https://github.com/2captcha/2captcha-python

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

solver = TwoCaptcha(api_key)

try:
    result = solver.normal('path/to/captcha.jpg')

except Exception as e:
    sys.exit(e)

else:
    sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
    // https://github.com/2captcha/2captcha-csharp

    using System;
    using System.Linq;
    using TwoCaptcha.Captcha;

    namespace TwoCaptcha.Examples
    {
        public class NormalExample
        {
            public static void Main()
            {
                var solver = new TwoCaptcha("YOUR_API_KEY");
                Normal captcha = new Normal("path/to/captcha.jpg");
                try
                {
                    solver.Solve(captcha).Wait();
                    Console.WriteLine("Captcha solved: " + captcha.Code);
                }
                catch (AggregateException e)
                {
                    Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
                }
            }
        }
    }
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
    // https://github.com/2captcha/2captcha-java

    package examples;

    import com.twocaptcha.TwoCaptcha;
    import com.twocaptcha.captcha.Normal;

    public class NormalExample {
        public static void main(String[] args) {
            TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
            Normal captcha = new Normal("path/to/captcha.jpg");
            try {
                solver.solve(captcha);
                System.out.println("Captcha solved: " + captcha.getCode());
            } catch (Exception e) {
                System.out.println("Error occurred: " + e.getMessage());
            }
        }

    }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
    // https://github.com/2captcha/2captcha-go

    package main

    import (
        "fmt"
        "log"
        "github.com/2captcha/2captcha-go"
    )

    func main() {
        client := api2captcha.NewClient("API_KEY")
        captcha := api2captcha.Normal{
            File: "/path/to/captcha.jpg",
        }
        code, err := client.Solve(captcha.ToRequest())
        if err != nil {
            log.Fatal(err);
        }
        fmt.Println("code "+code)
    }
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
    require 'api_2captcha'

    client =  Api2Captcha.new("YOUR_API_KEY")

    result = client.normal({ image: 'path/to/captcha.jpg'})
    # OR
    result = client.normal({
    image: 'https://site-with-captcha.com/path/to/captcha.jpg'
    })
  ```
  </div>
</div>

---

# Other methods

## test method

The method can be used for debugging. It allows to check the parameters of your request and see how our API service sees your request.

**API Endpoint:** `https://api.2captcha.com/test`
**Method:** `POST`
**Content-Type:** `application/json`

### Request example

```json
{
    "clientKey": "YOUR_API_KEY",
    "foo": "bar",
    "test": true,
    "attempt": 3,
    "options": {
        "list": [
            "item1",
            "item2"
        ]
    }
}
```

### Response example

```
Parsed input JSON:
Dict
(
[clientKey] => YOUR_API_KEY
[foo] => bar
[test] => 1
[attempt] => 3
[options] => Dict
(
[list] => Dict
(
[0] => item1
[1] => item2
)

)

)
Raw POST input:
{
"clientKey": "YOUR_API_KEY",
"foo": "bar",
"test": true,
"attempt": 3,
"options": {
"list": [
"item1",
"item2"
]
}
}
```


There are few methods made for compatibility with different software and libraries.

- `reportCorrectRecaptcha` - alias for [`reportCorrect`](/api-docs/report-correct)
- `reportIncorrectImageCaptcha` - alias for [`reportIncorrect`](/api-docs/report-incorrect)
- `reportIncorrectRecaptcha` - alias for [`reportIncorrect`](/api-docs/report-incorrect)

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/prosopo-procaptcha.svg" width="320" height="160" alt="Prosopo Procaptcha" />

<h1>Prosopo Procaptcha</h1>

</div>

Token-based method to bypass Prosopo Procaptcha.



## Task types
- **ProsopoTaskProxyless** - we use our own pool of proxies
- **ProsopoTask** - we use your proxies

## ProsopoTaskProxyless task type specification

| Property                | Type     | Required | Description |
| ----------------------- | -------- | -------- | ----------- |
| **type**                | *String* | **Yes**  | Task type: <br>**ProsopoTaskProxyless** <br>  **ProsopoTask** |
| **websiteURL**          | *String* | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
|  **websiteKey**         | *String* | **Yes**  | The value of `siteKey` parameter found on the page |


## ProsopoTask task type specification

`ProsopoTask` extends `ProsopoTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### ProsopoTaskProxyless

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"ProsopoTaskProxyless",
        "websiteKey":"5EPQoMZEDc5LpN7gtxMMzYPTzA6UeWqL2stk1rso9gy4Ahqt",
        "websiteURL":"https://www.example.com/"
    }
}
```

### ProsopoTask

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"ProsopoTask",
        "websiteKey":"5EPQoMZEDc5LpN7gtxMMzYPTzA6UeWqL2stk1rso9gy4Ahqt",
        "websiteURL":"https://www.example.com/",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": "8080",
        "proxyLogin": "user23",
        "proxyPassword": "p4$w0rd"
    }
}
```


## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "0x00016c68747470733a2f2f70726f6e6f6465332e70726f736f706f2e696fc0354550516f4d5a454463354c704e376774784d4d7a5950547a4136..."
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

---

# Using proxies

Proxies can be used to solve most types of javascript-based captchas:

* [reCAPTCHA v2](/api-docs/recaptcha-v2)
* [reCAPTCHA Enterpise v2](/api-docs/recaptcha-v2-enterprise)
* [Arkose Labs FunCaptcha](/api-docs/arkoselabs-funcaptcha)
* [Geetest](/api-docs/geetest)
* [Geetest v4](/api-docs/geetest)
* [KeyCaptcha](/api-docs/keycaptcha)
* [Capy Puzzle](/api-docs/capy-puzzle-captcha)
* [Lemin Cropped Captcha](/api-docs/lemin)
* [Cloudflare Turnstile](/api-docs/cloudflare-turnstile)
* [Amazon WAF](/api-docs/amazon-aws-waf-captcha)
* [CyberSiARA](/api-docs/anti-cyber-siara)
* [MTCaptcha](/api-docs/mtcaptcha)
* [DataDome captcha](/api-docs/datadome-slider-captcha)
* [VK captcha](/api-docs/vk-captcha)

Proxy allows to solve the captcha from the same IP address as you load the page.  
Using proxies is not obligatory in most cases. But for some kind of protection you should use it. For example: Cloudflare and Datadome protection pages require IP matching.  
Also good proxies with regular rotation can raise the speed and success rate for [Arkose Labs FunCaptcha](#solving_funcaptcha_new).

Proxies are not supported for reCAPTCHA v3 and Enterprise v3 as proxies dramatically decrease the success rate for this types of captcha.

If you send us the proxy, we check it's availability trying to open the website through you proxy, and if we can't do that we will not use your proxy.  
If we're able to use your proxy - we'll load the reCAPTCHA through it for solving.

We have our own proxies that we can offer you. [Buy residential proxies](https://2captcha.com/proxy/residential-proxies) for avoid restrictions and blocks. [Quick start](https://2captcha.com/proxy?openAddTrafficModal=true).

We support the following proxy types: `SOCKS4`, `SOCKS5`, `HTTP`, `HTTPS` with authentication by IP address or login and password.

If your proxy uses IP authentication you have to add our IP addresses to the list of allowed IPs of the proxy:  
`138.201.188.166`

Then provide your proxy IP address and port as a value for _proxyAddress_ and _proxyPort_ parameters.    
And the type of your proxy as a value for _proxyType_ parameter.

If your proxy uses login/password authentication you have to include your credentials in _proxyLogin_ and _proxyPassword_ parameters.

#### POST parameters for proxies

| **POST parameter** | **Type** | **Required** | **Description** |
| ------------------ | -------- | ------------ | --------------- |
| **proxyType**      | *String* | **Yes**      | Type of your proxy: `HTTP`, `HTTPS`, `SOCKS4`, `SOCKS5`. <br>Example: _proxytype=SOCKS4_|
| **proxyAddress**   | *String* | **Yes**      | Proxy IP address or hostname                             |
| **proxyPort**      | *number* | **Yes**      | Proxy port                                               |
| proxyLogin         | *String* | No           | Login for basic authentication on the proxy              |
| proxyPassword      | *String* | No           | Password for basic authentication on the proxy           |

---

# Quick start

To use the API you need to obtain you API key from the [Dashboard](/enterpage).
The key is used to authenticate all your requests to the API endpoints.

For quick integration you can use one of the libraries:
- [Python](https://github.com/2captcha/2captcha-python)
- [PHP](https://github.com/2captcha/2captcha-php)
- [Java](https://github.com/2captcha/2captcha-java)
- [C++](https://github.com/2captcha/2captcha-cpp)
- [Go](https://github.com/2captcha/2captcha-go)
- [Ruby](https://github.com/2captcha/2captcha-ruby)
- [Node.js](https://github.com/2captcha/2captcha-javascript)

Or you can make HTTP requests directly to the API endpoints according to the specification.

## API Endpoints and Data Formats

### Endpoints

#### The main API endpoint is: `https://api.2captcha.com`

Request method: `POST`
Data format: `JSON`
Content-Type: `application/json`


## Basic Workflow

The process of interaction with the API:
1. Submit your task using [createTask](/api-docs/create-task) method and get the task id
2. Get the result for the task using [getTaskResult](/api-docs/get-task-result) method
3. Use the result according to your use-cases
4. Send feedback with [reportCorrect](/api-docs/report-correct) and [reportIncorrect](/api-docs/report-incorrect) methods

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/recaptcha-v2.svg" width="320" height="160" alt="reCAPTCHA v2 widget" />

<h1>reCAPTCHA Grid (Image Click)</h1>

</div>

This is a type of reCAPTCHA v2 where users need to select all images matching a given instruction (for example, "Select all squares with bicycles"). The image is divided into a grid (usually 3×3 or 4×4), and the appropriate cells are selected via the API **GridTask** method.

Returns an array of tile indices, where `0` corresponds to the top-left tile.

**Supported image formats:** JPEG, PNG, GIF  
**Maximum file size:** 600 kB  
**Maximum image dimensions:** 1000px on any side

---
## GridTask Specification

| Property        | Type     | Required | Description |
| --------------- | -------- | -------- | ----------- |
| **type**        | *String* | **Yes**  | Task type: **GridTask** |
| **body**        | *String* | **Yes**  | Image encoded in Base64. Data-URI format (with `data:content/type` prefix) is also supported |
| rows            | *Integer*| No       | Number of rows in the grid |
| columns         | *Integer*| No       | Number of columns in the grid |
| comment         | *String* | **Yes\***| Instruction text shown to workers to solve the captcha correctly |
| imgInstructions | *String* | **Yes\***| Instruction image displayed to workers. Must be Base64-encoded. Maximum file size: 100 kB |
| minClicks       | *Integer*| No       | Minimum number of tiles to be selected (default: `1`). Cannot exceed `rows * columns` |
| maxClicks       | *Integer*| No       | Maximum number of tiles to be selected (default: `rows * columns`) |
| canNoAnswer     | *Integer*| No       | `0` — not allowed<br>`1` — image may not contain any tiles matching the instruction. Set to `1` only if some images may have no correct tiles. Workers will see a "No matching images" button, and the response will contain `No_matching_images`. |
| previousId      | *String* | No       | ID of your previous request for the same reCAPTCHA task |
| imgType         | *String* | No       | Image will be processed via Computer Vision to speed up solving. Supported values: <br>`funcaptcha` — FunCaptcha version requiring a tile click. [More info](https://2captcha.com/blog/funcaptcha-bypass-2-ways-solutions).<br>`recaptcha` — reCAPTCHA. [More info](https://2captcha.com/blog/recaptcha-recognition-using-grid-method).<br>**Important:** when using `imgType`, always provide the `comment` parameter containing the original instruction in English and send the original image files rather than screenshots. |

- Either `comment` or `imgInstructions` must be provided.

---

### Example Request

Method: [createTask](/api-docs/create-task)  
API endpoint: `https://api.2captcha.com/createTask`

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "GridTask",
        "body": "/9j/4AAQSkZJRgABAQAAAQ..HIAAAAAAQwAABtbnRyUkdCIFhZ.wc5GOGSRF//Z",
        "imgType": "recaptcha",
        "comment": "select all vehicles",
        "rows": 4,
        "columns": 4
    }
}
```

### Example Response

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "click": [
            4,
            8,
            12,
            16
        ]
    },
    "cost": "0.0012",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

## Examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
    // https://github.com/2captcha/2captcha-php

    require(__DIR__ . '/../src/autoloader.php');

    $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

    try {
        $result = $solver->grid('path/to/captcha.jpg', ['imgType' => 'recaptcha']);
    } catch (\Exception $e) {
        die($e->getMessage());
    }

    die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
# https://github.com/2captcha/2captcha-python

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from twocaptcha import TwoCaptcha

api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

solver = TwoCaptcha(api_key)

try:
    result = solver.grid('path/to/captcha.jpg', imgType='recaptcha')

except Exception as e:
    sys.exit(e)

else:
    sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
    // https://github.com/2captcha/2captcha-csharp

    using System;
    using System.Linq;
    using TwoCaptcha.Captcha;

    namespace TwoCaptcha.Examples
    {
        public class GridExample
        {
            public static void Main()
            {
                var solver = new TwoCaptcha("YOUR_API_KEY");
                Grid captcha = new Grid("path/to/captcha.jpg");
                captcha.ImgType = "recaptcha"; 
                try
                {
                    solver.Solve(captcha).Wait();
                    Console.WriteLine("Captcha solved: " + captcha.Code);
                }
                catch (AggregateException e)
                {
                    Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
                }
            }
        }
    }
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
    // https://github.com/2captcha/2captcha-java

    package examples;

    import com.twocaptcha.TwoCaptcha;
    import com.twocaptcha.captcha.Grid;

    public class GridExample {
        public static void main(String[] args) {
            TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
            Grid captcha = new Grid("path/to/captcha.jpg");
            captcha.setImgType("recaptcha");
            try {
                solver.solve(captcha);
                System.out.println("Captcha solved: " + captcha.getCode());
            } catch (Exception e) {
                System.out.println("Error occurred: " + e.getMessage());
            }
        }

    }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
    // https://github.com/2captcha/2captcha-go

    package main

    import (
        "fmt"
        "log"
        "github.com/2captcha/2captcha-go"
    )

    func main() {
        client := api2captcha.NewClient("API_KEY")
        captcha := api2captcha.Grid{
            File: "/path/to/captcha.jpg",
            ImgType: "recaptcha",
        }

        code, err := client.Solve(captcha.ToRequest())
        if err != nil {
            log.Fatal(err);
        }
        fmt.Println("code "+code)
    }
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
    require 'api_2captcha'

    client =  Api2Captcha.new("YOUR_API_KEY")

    result = client.grid({
      image: 'path/to/captcha.jpg',
      imgType: 'recaptcha'
    })
  ```
  </div>
</div>

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/recaptcha-v2.svg" width="320" height="160" alt="reCAPTCHA v2 widget" />

<h1>reCAPTCHA v2</h1>

</div>

<div class="h-guides">
    <h2>How to guides</h2>
    <ul class="h-list">
        <li>
            <a href="/h/how-to-bypass-google-recaptcha">
                <img src="/assets/captcha-api-docs/img/recaptcha-thumbnail.svg" width="40" height="40" alt="reCAPTCHA" loading="lazy" />
                <span>How to bypass Google reCAPTCHA</span>
            </a>
        </li>
        <li>
            <a href="/h/recaptcha-v2-bypass">
                <img src="/assets/captcha-api-docs/img/recaptcha-thumbnail.svg" width="40" height="40" alt="reCAPTCHA" loading="lazy" />
                <span>How to bypass reCAPTCHA v2</span>
            </a>
        </li>
        <li>
            <a href="/h/recaptcha-v3-bypass">
                <img src="/assets/captcha-api-docs/img/recaptcha-thumbnail.svg" width="40" height="40" alt="reCAPTCHA" loading="lazy" />
                <span>How to bypass reCAPTCHA v3</span>
            </a>
        </li>
        <li>
            <a href="/h/recaptcha-v2-callback">
                <img src="/assets/captcha-api-docs/img/recaptcha-thumbnail.svg" width="40" height="40" alt="reCAPTCHA" loading="lazy" />
                <span>How to solve reCAPTCHA v2 callback</span>
            </a>
        </li>
    </ul>
</div>

Token-based method for automated solving of reCAPTCHA v2.

The token recived then can be sent to the target website inside `g-recaptcha-response` form field or passed to a callback function.


## Task types
- **RecaptchaV2TaskProxyless** - suitable for most cases. We use our own pool of proxies to solve the captchas
- **RecaptchaV2Task** - used for cases when IP matching is requied on Google service like Google Search, YouTube, etc. Bad proxies will drastically decrease the success rate and increase the solving time.

## RecaptchaV2TaskProxyless task type specification

| Property            | Type      | Required | Description|
| ------------------- | --------- | -------- | ---------- |
| **type**            | *String*  | **Yes**  | Task type: <br>**RecaptchaV2TaskProxyless** <br>  **RecaptchaV2Task** |
| **websiteURL**      | *String*  | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **websiteKey**      | *String*  | **Yes**  | reCAPTCHA sitekey. Can be found inside `data-sitekey` property of the reCAPTCHA `div` element or inside `k` parameter of the requests to reCAPTHCHA API. You can also use the [script](https://gist.github.com/2captcha/2ee70fa1130e756e1693a5d4be4d8c70) to find the value |
| recaptchaDataSValue | *String*  | No       | The value of `data-s` parameter. Can be required to bypass the captcha on Google services |
| isInvisible         | *Boolean* | No       | Pass `true` for Invisible version of reCAPTCHA - a case when you don't see the checkbox, but the challenge appears. Mostly used with a callback function |
| userAgent           | *String*  | No       | User-Agent of your browser will be used to load the captcha. Use only modern browser's User-Agents |
| cookies             | *String*    | No       | Your cookies will be set in a browser of our worker. Suitable for captcha on Google services. The format is: `key1=val1; key2=val2`|
| apiDomain           | *String*  | No       | Domain used to load the captcha: `google.com` or `recaptcha.net`. Default value: `google.com`|


## RecaptchaV2Task task type specification

`RecaptchaV2Task` extends `RecaptchaV2TaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### RecaptchaV2TaskProxyless

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"RecaptchaV2TaskProxyless",
        "websiteURL":"https://2captcha.com/demo/recaptcha-v2",
        "websiteKey":"6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
        "isInvisible":false
    }
}
```

### RecaptchaV2Task

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"RecaptchaV2Task",
        "websiteURL":"https://2captcha.com/demo/recaptcha-v2",
        "websiteKey":"6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
        "isInvisible":false,
        "userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "cookies":"foo=bar; baz=1",
        "proxyType":"http",
        "proxyAddress":"1.2.3.4",
        "proxyPort":"8080",
        "proxyLogin":"user23",
        "proxyPassword":"p4$w0rd"
    }
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "gRecaptchaResponse": "03ADUVZw...UWxTAe6ncIa",
        "token": "03ADUVZw...UWxTAe6ncIa"
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```


## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
  // https://github.com/2captcha/2captcha-php

  require(__DIR__ . '/../src/autoloader.php');

  $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

  try {
      $result = $solver->recaptcha([
          'sitekey' => '6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u',
          'url'     => 'https://2captcha.com/demo/recaptcha-v2',
      ]);
  } catch (\Exception $e) {
      die($e->getMessage());
  }

  die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
  # https://github.com/2captcha/2captcha-python

  import sys
  import os

  sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

  from twocaptcha import TwoCaptcha

  api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

  solver = TwoCaptcha(api_key)

  try:
      result = solver.recaptcha(
          sitekey='6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u',
          url='https://2captcha.com/demo/recaptcha-v2')

  except Exception as e:
      sys.exit(e)

  else:
      sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
  // https://github.com/2captcha/2captcha-csharp

  using System;
  using System.Linq;
  using TwoCaptcha.Captcha;

  namespace TwoCaptcha.Examples
  {
      public class reCAPTCHAV2Example
      {
          public void Main()
          {
              TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
              ReCaptcha captcha = new ReCaptcha();
              captcha.SetSiteKey("6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u");
              captcha.SetUrl("https://2captcha.com/demo/recaptcha-v2");
              try
              {
                  solver.Solve(captcha).Wait();
                  Console.WriteLine("Captcha solved: " + captcha.Code);
              }
              catch (AggregateException e)
              {
                  Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
              }
          }
      }
  }
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
  // https://github.com/2captcha/2captcha-java

  package examples;

  import com.twocaptcha.TwoCaptcha;
  import com.twocaptcha.captcha.reCAPTCHA;

  public class reCAPTCHAV2Example {
      public static void main(String[] args) {
          TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
          ReCaptcha captcha = new ReCaptcha();
          captcha.setSiteKey("6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u");
          captcha.setUrl("https://2captcha.com/demo/recaptcha-v2");
          try {
              solver.solve(captcha);
              System.out.println("Captcha solved: " + captcha.getCode());
          } catch (Exception e) {
              System.out.println("Error occurred: " + e.getMessage());
          }
      }

  }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
  // https://github.com/2captcha/2captcha-go

  package main

  import (
      "fmt"
      "log"
      "github.com/2captcha/2captcha-go"
  )

  func main() {
      client := api2captcha.NewClient("API_KEY")
      captcha := api2captcha.ReCaptcha{
          SiteKey: "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
          Url: "https://2captcha.com/demo/recaptcha-v2",
      } 
      code, err := client.Solve(captcha.ToRequest())
      if err != nil {
          log.Fatal(err);
      }
      fmt.Println("code "+code)
  }
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
  # https://github.com/2captcha/2captcha-ruby

  require 'api_2captcha'

  client =  Api2Captcha.new("YOUR_API_KEY")

  result = client.recaptcha_v2({
    googlekey: '6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u',
    pageurl: 'https://2captcha.com/demo/recaptcha-v2'
  })
  ```
  </div>
</div>

## Useful links

* [Demo page reCAPTCHA v2](https://2captcha.com/demo/recaptcha-v2)
* [How to bypass reCAPTCHA v2](https://2captcha.com/p/recaptcha_v2)
* [Description of using the `data-s` parameter on search pages google.com](https://2captcha.com/blog/bypassing-recaptcha-v2-on-google-search)
* [Video how to bypass reCAPTCHA v2](https://www.youtube.com/watch?v=zOmhDxRqX18)
* [Script for finding captcha parameters](https://gist.github.com/2captcha/2ee70fa1130e756e1693a5d4be4d8c70)

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/recaptcha-enterprise.svg" width="320" height="160" alt="reCAPTCHA v2 Enterprise widget" />

<h1>reCAPTCHA v2 Enterprise</h1>

</div>

Token-based method for automated solving of reCAPTCHA v2 Enterprise.


The token recived then can be sent to the target website inside `g-recaptcha-response` form field or passed to a callback function. The method is the same as reCAPTCHA v2, but [reCAPTCHA Enterprise API](https://cloud.google.com/recaptcha-enterprise/docs) is used to load the captchas.


## Task types
- **RecaptchaV2EnterpriseTaskProxyless** - suitable for most cases. We use our own pool of proxies to solve the captchas
- **RecaptchaV2EnterpriseTask** - used for cases when IP matching is requied on Google service like Google Search, YouTube, etc. Bad proxies will drastically decrease the success rate and increase the solving time.

## RecaptchaV2EnterpriseTaskProxyless task type specification

| Property          | Type      | Required | Description |
| ----------------- | --------- | -------- | ----------- |
| **type**          | *String*  | **Yes**  | Task type: <br>**RecaptchaV2EnterpriseTaskProxyless** <br> **RecaptchaV2EnterpriseTask** |
| **websiteURL**    | *String*  | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **websiteKey**    | *String*  | **Yes**  | reCAPTCHA sitekey. Can be found inside `data-sitekey` property of the reCAPTCHA `div` element or inside `k` parameter of the requests to reCAPTHCHA API. You can also use the [script](https://gist.github.com/2captcha/2ee70fa1130e756e1693a5d4be4d8c70) to find the value |
| enterprisePayload | *Object*  | No       | Additional parameters passed to `grecaptcha.enterprise.render` call. For example, there can be an object containing `s` value |
| isInvisible       | *Boolean* | No       | Pass `true` for Invisible version of reCAPTCHA - a case when you don't see the checkbox, but the challenge appears. Mostly used with a callback function |
| userAgent         | *String*  | No       | User-Agent of your browser will be used to load the captcha. Use only modern browser's User-Agents |
| cookies           | *String*    | No       | Your cookies will be set in a browser of our worker. Suitable for captcha on Google services. The format is: `key1=val1; key2=val2` |
| apiDomain         | *String*  | No       | Domain used to load the captcha: `google.com` or `recaptcha.net`. Default value: `google.com` |


## RecaptchaV2EnterpriseTask task type specification

`RecaptchaV2EnterpriseTask` extends `RecaptchaV2EnterpriseTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### RecaptchaV2EnterpriseTaskProxyless

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"RecaptchaV2EnterpriseTaskProxyless",
        "websiteURL":"https://2captcha.com/demo/recaptcha-v2-enterprise",
        "websiteKey":"6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
        "isInvisible":false
    }
}
```

### RecaptchaV2Task

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type":"RecaptchaV2EnterpriseTask",
        "websiteURL":"https://2captcha.com/demo/recaptcha-v2-enterprise",
        "websiteKey":"6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
        "isInvisible":false,
        "userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "cookies":"foo=bar; baz=1",
        "proxyType":"http",
        "proxyAddress":"1.2.3.4",
        "proxyPort":"8080",
        "proxyLogin":"user23",
        "proxyPassword":"p4$w0rd"
    }
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "gRecaptchaResponse": "03ADUVZw...UWxTAe6ncIa",
        "token": "03ADUVZw...UWxTAe6ncIa"
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556
}
```


## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="recaptcha-v2-php-code-example" data-component="TabPanel">

  ```php
  // https://github.com/2captcha/2captcha-php

  require(__DIR__ . '/../src/autoloader.php');

  $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

  try {
      $result = $solver->recaptcha([
          'sitekey' => '6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u',
          'url'     => 'https://2captcha.com/demo/recaptcha-v2-enterprise-enterprise',
          'enterprise' => 1,
      ]);
  } catch (\Exception $e) {
      die($e->getMessage());
  }

  die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="recaptcha-v2-python-code-example" data-component="TabPanel">

  ```python
  # https://github.com/2captcha/2captcha-python

  import sys
  import os

  sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

  from twocaptcha import TwoCaptcha

  api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

  solver = TwoCaptcha(api_key)

  try:
      result = solver.recaptcha(
          sitekey='6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u',
          url='https://2captcha.com/demo/recaptcha-v2-enterprise',
          enterprise=1)

  except Exception as e:
      sys.exit(e)

  else:
      sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="recaptcha-v2-csharp-code-example" data-component="TabPanel">

  ```csharp
  // https://github.com/2captcha/2captcha-csharp

  using System;
  using System.Linq;
  using TwoCaptcha.Captcha;

  namespace TwoCaptcha.Examples
  {
      public class reCAPTCHAV2EnterpriseExample
      {
          public void Main()
          {
              TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
              ReCaptcha captcha = new ReCaptcha();
              captcha.SetSiteKey("6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u");
              captcha.SetUrl("https://2captcha.com/demo/recaptcha-v2-enterprise");
              captcha.setEnterprise(true);
              try
              {
                  solver.Solve(captcha).Wait();
                  Console.WriteLine("Captcha solved: " + captcha.Code);
              }
              catch (AggregateException e)
              {
                  Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
              }
          }
      }
  }
  ```
  </div>

  <div id="recaptcha-v2-java-code-example" data-component="TabPanel">

  ```java
  // https://github.com/2captcha/2captcha-java

  package examples;

  import com.twocaptcha.TwoCaptcha;
  import com.twocaptcha.captcha.reCAPTCHA;

  public class reCAPTCHAV2EnterpriseExample {
      public static void main(String[] args) {
          TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
          ReCaptcha captcha = new ReCaptcha();
          captcha.setSiteKey("6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u");
          captcha.setUrl("https://2captcha.com/demo/recaptcha-v2-enterprise");
          captcha.setEnterprise(true);
          try {
              solver.solve(captcha);
              System.out.println("Captcha solved: " + captcha.getCode());
          } catch (Exception e) {
              System.out.println("Error occurred: " + e.getMessage());
          }
      }

  }
  ```
  </div>

  <div id="recaptcha-v2-go-code-example" data-component="TabPanel">

  ```go
  // https://github.com/2captcha/2captcha-go

  package main

  import (
      "fmt"
      "log"
      "github.com/2captcha/2captcha-go"
  )

  func main() {
      client := api2captcha.NewClient("API_KEY")
      captcha := api2captcha.ReCaptcha{
          SiteKey: "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u",
          Url: "https://2captcha.com/demo/recaptcha-v2-enterprise",
          Enterprise: true,
      } 
      code, err := client.Solve(captcha.ToRequest())
      if err != nil {
          log.Fatal(err);
      }
      fmt.Println("code "+code)
  }
  ```
  </div>

  <div id="recaptcha-v2-ruby-code-example" data-component="TabPanel">

  ```ruby
  # https://github.com/2captcha/2captcha-ruby

  require 'api_2captcha'

  client =  Api2Captcha.new("YOUR_API_KEY")

  result = client.recaptcha_v2({
    googlekey: '6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u',
    pageurl: 'https://2captcha.com/demo/recaptcha-v2-enterprise',
    enterprise: 1
  })
  ```
  </div>
</div>

## Useful links

* [Demo page reCAPTCHA v2 Enterprise](https://2captcha.com/demo/recaptcha-v2-enterprise)
* [How to bypass reCAPTCHA Enterprise](https://2captcha.com/p/recaptcha_enterprise)
* [Script for finding captcha parameters](https://gist.github.com/2captcha/2ee70fa1130e756e1693a5d4be4d8c70)

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/recaptcha-v3.svg" width="320" height="160" alt="reCAPTCHA v3 widget" />

<h1>reCAPTCHA v3 / reCAPTCHA v3 Enterprise</h1>

</div>

Token-based method for automated solving of reCAPTCHA v3.

The token recived then can be sent to the target website inside `g-recaptcha-response` form field or passed to a callback function.


### Task type: RecaptchaV3TaskProxyless

## RecaptchaV3TaskProxyless task type specification

| Property       | Type      | Required | Description |
| -------------- | --------- | -------- | ----------- |
| **type**       | *String*  | **Yes**  | Task type: <br>**RecaptchaV3TaskProxyless** |
| **websiteURL** | *String*  | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **websiteKey** | *String*  | **Yes**  | reCAPTCHA sitekey. Can be found inside `data-sitekey` property of the reCAPTCHA `div` element or inside `k` parameter of the requests to reCAPTHCHA API. You can also use the [script](https://gist.github.com/2captcha/2ee70fa1130e756e1693a5d4be4d8c70) to find the value |
| **minScore**   | *Float*   | Yes      | Required score value: <br> **0.3** <br> **0.7** <br> **0.9** |
| pageAction     | *String*  | No       | Action parameter value. The value is set by website owner inside `data-action` property of the reCAPTCHA `div` element or passed inside options object of `execute` method call, like `grecaptcha.execute('websiteKey'{ action: 'myAction' })` |
| isEnterprise   | *Boolean* | No       | Pass `true` for Enterprise version of reCAPTCHA. You can identify it by `enterprise.js` script used instead of `api.js` or by `grecaptcha.enterprise.execute` call used instead of `grecaptcha.execute` |
| apiDomain      | *String*  | No       | Domain used to load the captcha: `google.com` or `recaptcha.net`. Default value: `google.com` |

## Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type": "RecaptchaV3TaskProxyless",
        "websiteURL": "https://2captcha.com/demo/recaptcha-v3",
        "websiteKey": "6LfB5_IbAAAAAMCtsjEHEHKqcB9iQocwwxTiihJu",
        "minScore": 0.9,
        "pageAction": "test",
        "isEnterprise": false,
        "apiDomain": "www.recaptcha.net"
    }
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "gRecaptchaResponse": "03ADUVZwB7eLoqnBxvi5H...kA4Si3qH0rR0g",
        "token": "03ADUVZwB7eLoqnBxvi5H...kA4Si3qH0rR0g"
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```


## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
  // https://github.com/2captcha/2captcha-php

  require(__DIR__ . '/../src/autoloader.php');

  $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

  try {
      $result = $solver->recaptcha([
          'sitekey' => '6LfB5_IbAAAAAMCtsjEHEHKqcB9iQocwwxTiihJu',
          'url'     => 'https://2captcha.com/demo/recaptcha-v3',
          'version' => 'v3',
          'action'  => 'test',
      ]);
  } catch (\Exception $e) {
      die($e->getMessage());
  }

  die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
  # https://github.com/2captcha/2captcha-python

  import sys
  import os

  sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

  from twocaptcha import TwoCaptcha

  api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

  solver = TwoCaptcha(api_key)

  try:
      result = solver.recaptcha(
          sitekey='6LfB5_IbAAAAAMCtsjEHEHKqcB9iQocwwxTiihJu',
          url='https://2captcha.com/demo/recaptcha-v3',
          version='v3',
          action='test')

  except Exception as e:
      sys.exit(e)

  else:
      sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
  // https://github.com/2captcha/2captcha-csharp

  using System;
  using System.Linq;
  using TwoCaptcha.Captcha;

  namespace TwoCaptcha.Examples
  {
      public class reCAPTCHAV3Example
      {
          public void Main()
          {
              TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
              ReCaptcha captcha = new ReCaptcha();
              captcha.SetSiteKey("6LfB5_IbAAAAAMCtsjEHEHKqcB9iQocwwxTiihJu");
              captcha.SetUrl("https://2captcha.com/demo/recaptcha-v3");
              captcha.SetVersion("v3");
              captcha.SetAction("test");
              try
              {
                  solver.Solve(captcha).Wait();
                  Console.WriteLine("Captcha solved: " + captcha.Code);
              }
              catch (AggregateException e)
              {
                  Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
              }
          }
      }
  }
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
  // https://github.com/2captcha/2captcha-java

  package examples;

  import com.twocaptcha.TwoCaptcha;
  import com.twocaptcha.captcha.reCAPTCHA;

  public class reCAPTCHAV3Example {
      public static void main(String[] args) {
          TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
          ReCaptcha captcha = new ReCaptcha();
          captcha.setSiteKey("6LfB5_IbAAAAAMCtsjEHEHKqcB9iQocwwxTiihJu");
          captcha.setUrl("https://2captcha.com/demo/recaptcha-v3");
          captcha.setVersion("v3");
          captcha.setAction("test");
          try {
              solver.solve(captcha);
              System.out.println("Captcha solved: " + captcha.getCode());
          } catch (Exception e) {
              System.out.println("Error occurred: " + e.getMessage());
          }
      }

  }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
  // https://github.com/2captcha/2captcha-go

  package main

  import (
      "fmt"
      "log"
      "github.com/2captcha/2captcha-go"
  )

  func main() {
      client := api2captcha.NewClient("API_KEY")
      captcha := api2captcha.ReCaptcha{
          SiteKey: "6LfB5_IbAAAAAMCtsjEHEHKqcB9iQocwwxTiihJu",
          Url: "https://2captcha.com/demo/recaptcha-v3",
          Version: "v3",
          Action: "verify"
      } 
      code, err := client.Solve(captcha.ToRequest())
      if err != nil {
          log.Fatal(err);
      }
      fmt.Println("code "+code)
  }
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
  # https://github.com/2captcha/2captcha-ruby

  require 'api_2captcha'

  client =  Api2Captcha.new("YOUR_API_KEY")

  result = client.recaptcha_v3({
    googlekey: '6LfB5_IbAAAAAMCtsjEHEHKqcB9iQocwwxTiihJu',
    pageurl: 'https://2captcha.com/demo/recaptcha-v3',
    version: 'v3',
    score: 0.9
  })
  ```
  </div>
</div>

## Useful links

* [Demo page reCAPTCHA v3](https://2captcha.com/demo/recaptcha-v3)
* [How to bypass reCAPTCHA v3](https://2captcha.com/p/recaptcha_v3)
* [reCAPTCHA v3 resolution - a tutorial for developers and customers](https://2captcha.com/blog/recaptcha-v3-automatic-resolution)
* [Video how to bypass reCAPTCHA v3](https://www.youtube.com/watch?v=0tYFZp_EVbQ)
* [Script for finding captcha parameters](https://gist.github.com/2captcha/2ee70fa1130e756e1693a5d4be4d8c70)

---

# reportCorrect method

The method is used for automated feedback on captcha solutions.
If the answer was accepted by the target website send this request. We use the collected statistics to make our service better.

**API Endpoint:** `https://api.2captcha.com/reportCorrect`
**Method:** `POST`
**Content-Type:** `application/json`

## Request properties

| Name          | Type   | Required | Description                |
| ------------- | ------ | -------- | -------------------------- |
| **clientKey** | *String* | **Yes**  | Your [API key](/enterpage) |
| **taskId**    | *Integer*| **Yes**  | The id of your task        |

## Request example

```json
{
   "clientKey": "YOUR_API_KEY",
   "taskId": 74455221488
}
```

## Response example

```json
{
    "errorId": 0,
    "status": "success"
}
```

---

# reportIncorrect method

The method is used for automated feedback on captcha solutions.
Make this request if the answer was **declined** by the target website. We use the collected statistics to improve our service, we check the solutions, we check workers who provided the solution and after the analisys we issue refunds for incorrectly solved captchas.

If your success rate is close to 0% please do not send this request, there is definetely wrong with your code/software.

## Refund Policy for Unsolved Captchas:

**Please note** that each complaint about a solved captcha is reviewed individually.

For standard captchas, we verify the accuracy of the provided answer. For token-based captchas, we analyze the performance metrics and statistics of the worker who provided the solution.

Based on this review, a decision is made regarding the eligibility for a refund.

Therefore, a refund is not guaranteed for every complaint, and the total refund amount may differ from the number of requests submitted.

**API Endpoint:** `https://api.2captcha.com/reportIncorrect`
**Method:** `POST`
**Content-Type:** `application/json`

## Request properties

| Name          | Type    | Required | Description                |
| ------------- | ------- | -------- | -------------------------- |
| **clientKey** | *String*  | **Yes**  | Your [API key](/enterpage) |
| **taskId**    | *Integer* | **Yes**  | The id of your task        |

## Request example

```json
{
   "clientKey": "YOUR_API_KEY",
   "taskId": 74455221488
}
```

## Response example

```json
{
    "errorId": 0,
    "status": "success"
}
```

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/rotate.svg" width="320" height="160" alt="Rotate" />

<h1>Rotate captcha</h1>

</div>

The method is used to solve captchas where you need to rotate an object to place it properly. Returns the required rotation angle.

**Supported image formats:** JPEG, PNG, GIF
**Max file size:** 600 kB
**Max image size:** 1000px on any side

## RotateTask type specification

| Property        | Type     | Required| Description    |
| --------------- | -------- | ------- | -------------- |
| **type**        | *String* | **Yes** | **RotateTask** |
| **body**        | *String* | **Yes** | Image encoded into Base64 format. Data-URI format (containing `data:content/type` prefix) is also supported |
| angle           | *Integer*| No      | One step rotation angle. You can count how many steps are required to rotate the image 360 degrees and then divide 360 by this count to get the angle value |
| comment         | *String* | No      | A comment will be shown to workers to help them to solve the captcha properly |
| imgInstructions | *String* | No      | An optional image with instruction that will be shown to workers. Image should be encoded into Base64 format. Max file size: 100 kB |




## Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

```json
{
    "clientKey":"YOUR_API_KEY",
    "task": {
        "type": "RotateTask",
        "body": "R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==",
        "comment": "position the image properly",
        "angle": 60
    },
    "languagePool": "en"
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "rotate": 180
    },
    "cost": "0.0005",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
  // https://github.com/2captcha/2captcha-php

  require(__DIR__ . '/../src/autoloader.php');

  $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

  try {
      $result = $solver->rotate([
          'file'  => 'path/to/captcha.jpg',
          'angle' => 15,
      ]);
  } catch (\Exception $e) {
      die($e->getMessage());
  }

  die('Captcha solved: ' . $result->code);
  ```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
  # https://github.com/2captcha/2captcha-python

  import sys
  import os

  sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

  from twocaptcha import TwoCaptcha

  api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

  solver = TwoCaptcha(api_key)

  try:
    result = solver.rotate('./images/rotate.jpg')

  except Exception as e:
  sys.exit(e)

  else:
    sys.exit('result: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
  // https://github.com/2captcha/2captcha-csharp

  using System;
  using System.Linq;
  using TwoCaptcha.Captcha;

  namespace TwoCaptcha.Examples
  {
      public class RotateExample
      {
          public void Main()
          {
              TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
              Rotate captcha = new Rotate();
              captcha.SetFile("path/to/captcha.jpg");
              captcha.SetAngle(15);
              try
              {
                  solver.Solve(captcha).Wait();
                  Console.WriteLine("Captcha solved: " + captcha.Code);
              }
              catch (AggregateException e)
              {
                  Console.WriteLine("Error occurred: " + e.InnerExceptions.First().Message);
              }
          }
      }
  }
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
  // https://github.com/2captcha/2captcha-java

  package examples;

  import com.twocaptcha.TwoCaptcha;
  import com.twocaptcha.captcha.Rotate;

  public class RotateExample {
      public static void main(String[] args) {
          TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
          Rotate captcha = new Rotate();
          captcha.setFile("path/to/captcha.jpg");
          captcha.setAngle(15);
          try {
              solver.solve(captcha);
              System.out.println("Captcha solved: " + captcha.getCode());
          } catch (Exception e) {
              System.out.println("Error occurred: " + e.getMessage());
          }
      }
  }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
// https://github.com/2captcha/2captcha-go

package main

import (
    "fmt"
    "log"
    "github.com/2captcha/2captcha-go"
)

func main() {
    client := api2captcha.NewClient("API_KEY")
    captcha := api2captcha.Rotate{
        File: "path/to/captcha.jpg",
        Angle: 15,
    }
    code, err := client.Solve(captcha.ToRequest())
    if err != nil {
        log.Fatal(err);
    }
    fmt.Println("code "+code)
}
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
  # https://github.com/2captcha/2captcha-ruby
  require 'api_2captcha'

  client =  Api2Captcha.new("YOUR_API_KEY")

  result = client.rotate({
    image: 'path/to/captcha.jpg',
    angle: 40,
    lang: 'en',
    hint_image: 'path/to/hint.jpg',
    hint_text: 'Put the images in the correct way'
  })
  ```
  </div>
</div>

## Useful links

- [Rotate captcha demo](/demo/rotatecaptcha)
- [How to solve rotate captcha](/p/rotatecaptcha)
- [Video how to solve rotate captcha](https://youtu.be/TWHid_mjuBo?si=5bTDBNG2k8nE92Rg)

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/temu_captcha.svg" width="320" height="160" alt="Temu captcha" />

<h1>Temu captcha</h1>

</div>

## Image-based method to bypass Temu captcha

- **TemuImageTask** - we use the `image` (image in base64 format) and `parts` - images of the response parts that need to be moved.
You need to get all the images and convert them to Base64-encoded strings.


## TemuCaptchaTask task type specification

| Property             | Type     | Required   | Description                                          |
| -------------------- | -------- | ---------- | ---------------------------------------------------- |
| **type**             | *String* | **Yes**    | Task type: <br>**TemuCaptchaTask**                   |
| **image**            | *String* | **Yes**    | Main background image as base64-encoded string       |
| **parts**            | *Array*  | **Yes**    | An array of movable image pieces in base64 format  |

## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### TemuImageTask

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"TemuImageTask",
        "image":"/9j/4AAQSkZJRg......",
        "parts":[
            "part1_b64",
            "part2_b64",
            "part3_b64"
        ]
    }
}
```
The query will return the ID of your captcha, which should be used to get the result.

```json
{
   "errorId": 0, 
   "taskId": 80306543329
}
```

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "cost": "0.0012",
    "createTime": 1754563182,
    "endTime": 1754563190,
    "errorId": 0,
    "ip": "46.53.232.76",
    "solution": {
        "coordinates": [
            {
                "x": 155,
                "y": 358
            },
            {
                "x": 152,
                "y": 153
            },
            {
                "x": 251,
                "y": 333
            }
        ]
    },
    "solveCount": 1,
    "status": "ready"
}
```

Use the received coordinates to position the image pieces correctly.

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/tencent.svg" width="320" height="160" alt="Tencent" />

<h1>Tencent (TenDI)</h1>

</div>

Token-based method to bypass Tencent captcha (TenDI).



## Task types
- **TencentTaskProxyless** - we use our own pool of proxies
- **TencentTask** - we use your proxies

## TencentTaskProxyless task type specification

| Property                | Type     | Required | Description |
| ----------------------- | -------- | -------- | ----------- |
| **type**                | *String* | **Yes**  | Task type: <br>**TencentTaskProxyless** <br>  **TencentTask** |
| **websiteURL**          | *String* | **Yes**  | The full URL of target web page where the captcha is loaded. We do not open the page, not a problem if it is available only for authenticated users |
| **appId**               | *String* | **Yes**  | The value of `appId` parameter in the website source code. |
| captchaScript           | *String* | **No**   | Captcha script URL from the page source code. Default: `https://turing.captcha.qcloud.com/TCaptcha.js` |


## TencentTask task type specification

`TencentTask` extends `TencentTaskProxyless` adding a set of proxy-related parameters listed below

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **socks4** <br> **socks5** |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### TencentTaskProxyless

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"TencentTaskProxyless",
        "appId":"190014885",
        "websiteURL":"https://www.example.com/"
    }
}
```

### TencentTask

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"TencentTask",
        "appId":"190014885",
        "websiteURL":"https://www.example.com/",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": "8080",
        "proxyLogin": "user23",
        "proxyPassword": "p4$w0rd"
    }
}
```


## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "appid": "190014885",
        "ret": 0,
        "ticket": "tr0344YjJASGmJGtohyWS_y6tJKiqVPIdFgl87vWlVaQoueR8D6DH28go-i-VjeassM31SXO7D0*",
        "randstr": "@KVN"
    },
    "cost": "0.00299",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```

### Using the token

The token is passed to a callback function defined in 2nd argument of `TencentCaptcha` constructor call during the captcha initialization. 

```js
new TencentCaptcha(CaptchaAppId, callback, options);
```

This function is usually used to make a request to the website backend where the token is verified. You can execute the callback function passing the token as an argument or build a request to the backend using passing the token.

For example, if the captcha is initialized like this:

```js
const myCallbackFunction = (token) {
    // verify the token
}
var captcha = new TencentCaptcha('190014885', myCallbackFunction, {});
captcha.show(); 
```

You need to call:

```js
let data = JSON.parse(res)
myCallbackFunction(res.solution)
```

Where `res` is the JSON response from the API.

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/text.svg" width="320" height="160" alt="Text Captcha" />

<h1>Text captcha</h1>

</div>

The method can be used to bypass tasks where you need to answer a question.
You can add some context that can help workers to provide the answer.


## TextCaptchaTask task type specification

| Property        | Type     | Required | Description         |
| --------------- | -------- | -------- | ------------------- |
| **type**        | *String* | **Yes**  | **TextCaptchaTask** |
| **comment**     | *String* | **Yes**  | Text with a question you need to answer. |


## Request example

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "TextCaptchaTask",
        "comment": "If tomorrow is Saturday, what day is today?"
    },
    "languagePool": "en"
}
```


### Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "text": "friday"
    },
    "cost": "0.001",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```


## Code examples

<div class="code-example" data-component="Tabs">
  <ul data-component="TabList">
  <li role="presentation">
  <a href="#php-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/php.svg" alt="" loading="lazy" />
  PHP
  </a>
  </li>
  <li role="presentation">
  <a href="#python-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/python.svg" alt="" loading="lazy"/>
  Python
  </a>
  </li>
  <li role="presentation">
  <a href="#csharp-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/csharp.svg" alt="" loading="lazy"/>
  C#
  </a>
  </li>
  <li role="presentation">
  <a href="#java-code-example" data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/java.svg" alt="" loading="lazy"/>
  Java
  </a>
  </li>
  <li role="presentation">
  <a href="#go-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/go.svg" alt="" loading="lazy"/>
  Go
  </a>
  </li>
  <li role="presentation">
  <a href="#ruby-code-example"  data-component="Tab">
  <img class="code-example-icon" src="/assets/captcha-recognition/icons/ruby.svg" alt="" loading="lazy"/>
  Ruby
  </a>
  </li>
  </ul>
  <div id="php-code-example" data-component="TabPanel">

  ```php
    // https://github.com/2captcha/2captcha-php

    require(__DIR__ . '/../src/autoloader.php');

    $solver = new \TwoCaptcha\TwoCaptcha('YOUR_API_KEY');

    try {
        $result = $solver->text([
            'text' => 'If tomorrow is Saturday, what day is today?',
            'lang' => 'en',
        ]);
    } catch (\Exception $e) {
        die($e->getMessage());
    }

    die('Captcha solved: ' . $result->code); 
```
  </div>

  <div id="python-code-example" data-component="TabPanel">

  ```python
    # https://github.com/2captcha/2captcha-python

    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    from twocaptcha import TwoCaptcha

    api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

    solver = TwoCaptcha(api_key, defaultTimeout=40, pollingInterval=10)

    try:
        result = solver.text('If tomorrow is Saturday, what day is today?',
                            lang='en')

    except Exception as e:
        sys.exit(e)

    else:
        sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="csharp-code-example" data-component="TabPanel">

  ```csharp
    // https://github.com/2captcha/2captcha-python

    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    from twocaptcha import TwoCaptcha

    api_key = os.getenv('APIKEY_2CAPTCHA', 'YOUR_API_KEY')

    solver = TwoCaptcha(api_key, defaultTimeout=40, pollingInterval=10)

    try:
        result = solver.text('If tomorrow is Saturday, what day is today?',
                            lang='en')

    except Exception as e:
        sys.exit(e)

    else:
        sys.exit('solved: ' + str(result))
  ```
  </div>

  <div id="java-code-example" data-component="TabPanel">

  ```java
    // https://github.com/2captcha/2captcha-java

    package examples;

    import com.twocaptcha.TwoCaptcha;
    import com.twocaptcha.captcha.Text;

    public class TextExample {
        public static void main(String[] args) {
            TwoCaptcha solver = new TwoCaptcha("YOUR_API_KEY");
            Text captcha = new Text();
            captcha.setText("If tomorrow is Saturday, what day is today?");
            captcha.setLang("en");
            try {
                solver.solve(captcha);
                System.out.println("Captcha solved: " + captcha.getCode());
            } catch (Exception e) {
                System.out.println("Error occurred: " + e.getMessage());
            }
        }
    }
  ```
  </div>

  <div id="go-code-example" data-component="TabPanel">

  ```go
    // https://github.com/2captcha/2captcha-go

    package main

    import (
        "fmt"
        "log"
        "github.com/2captcha/2captcha-go"
    )

    func main() {
        client := api2captcha.NewClient("API_KEY")
        captcha := api2captcha.Text{
            Text: "If tomorrow is Saturday, what day is today?",
            Lang: "en",
        }
        code, err := client.Solve(captcha.ToRequest())
        if err != nil {
            log.Fatal(err);
        }
        fmt.Println("code "+code)
    }
  ```
  </div>

  <div id="ruby-code-example" data-component="TabPanel">

  ```ruby
    require 'api_2captcha'

    client =  Api2Captcha.new("YOUR_API_KEY")

    result = client.text({
    textcaptcha:'If tomorrow is Saturday, what day is today?',
    lang: "en"
    })
  ```
  </div>
</div>



## Useful links
- [Text captcha demo](/demo/text)
- [How to solve text captcha](/p/text_captcha)
- [Video how to solve text captcha](https://youtu.be/Ytc0UoU_n3I)

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/tspd-captcha.svg" width="320" height="160" alt="Tspd" />

<h1>TSPD</h1>

</div>

A cookie based method for bypassing TSPD captcha.

## Task Types

* **TspdTask** — we use the proxy you provide

> **IMPORTANT**: For TSPD tasks, you must use a proxy with a static session. The same outbound IP address must be maintained across all stages, from getting cookies to solving the task and using those cookies afterward. Changing the IP or session between stages can cause errors.

## How It Works

1. First request. The script sends an HTTP request to the target page through your proxy, using browser like headers.

2. Getting cookies. The script extracts protection cookies from the server response. If the response contains the `TSPD_101_DID` cookie (meaning the protection was passed) or the cookie format is unexpected, the process stops.

3. Creating the task. The script sends the data to our service to solve the TSPD challenge.

4. Getting the solution. The script waits for the task to complete via the API and receives updated cookies.

5. Final request. The script makes another request to the page using the new cookies, and the server returns the regular HTML page.

## How to Find the Required Parameters

When you send a *GET* request to a page with a **TSPD challenge**, you will get HTML that needs to be Base64 encoded and passed in the `htmlPageBase64` parameter. Also, on the first request, the server will send special cookies (for example, `TS386a...400d029`). You must pass these in `tspdCookie` because they are required for the TSPD solution to work and for the API to respond correctly.

> **important**: The `htmlPageBase64` and `tspdCookie` parameters are dynamic. Extract them right before sending the task, otherwise the solution might fail.

**Please note**:

If the server returns cookies in one of these formats (3 to 4 lines):

```TS386a400d029=082670...87599c;
TS386a400d029=082670...40a8ea3;
TS386a400d078=082670...b4cbe2c;
TSd2153684027=082670...4415a6
```

or

```
TS386a400d029=08777...83ff9,
TS386a400d029=08777...fb459e,
TSd2153684027=08777...f0ad368
```

or

```
TS014d0691=01fef...1244b,
TS01fe94e8=01fef...9ed38,
TSafd868f7027=082670...a7ea7c
```

and there is no `TSPD_101_DID` cookie, this means the request was intercepted by the protection system and a block page (TSPD challenge) was returned instead of the normal content.

In this case, you need to:

1. Send the received cookies to our service,
2. Wait for the task to finish solving.
3. Use the updated cookies for all following requests.

## Specification for TspdTask

| Property           | Type     | Required | Description                                                            |
| ------------------ | -------- | ---------- | ------------------------------------------------------------------- |
| **type**           | *String* | **Yes**     | Task type: <br>**TspdTask**                                        |
| **websiteURL**     | *String* | **Yes**     | Full URL of the target web page where the captcha loads |
| **tspdCookie**     | *String* | **Yes**     | Cookies received on the TSPD challenge page                      |
| **htmlPageBase64** | *String* | **Yes**     | Full HTML of the TSPD challenge page, Base64 encoded                      |
| **proxyType**      | *String* | **Yes**     | Proxy type: <br>**http** <br> **socks4** <br> **socks5**            |
| **proxyAddress**   | *String* | **Yes**     | Proxy server IP address or hostname                               |
| **proxyPort**      | *Number*  | **Yes**     | Proxy server port                                                 |
| proxyLogin         | *String* | No        | Login for proxy authentication                          |
| proxyPassword      | *String* | No        | Password for proxy authentication                         |
| userAgent          | *String* | No        | Browser User-Agent used to load the page                 |

## Request Examples

Method: [createTask](/api-docs/create-task)
API Endpoint: `https://api.2captcha.com/createTask`

### TspdTask Request Example

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
      "type": "TspdTask",
      "websiteURL": "https://example.com/login",
      "tspdCookie": "TS386a400d029=082670...010245; TS386a400d078=082670...dbb3b0c",
      "htmlPageBase64": "PCFET0NUWVBFIGh0bWw+...",
      "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
      "proxyType": "http",
      "proxyAddress": "1.2.3.4",
      "proxyPort": 8080,
      "proxyLogin": "login",
      "proxyPassword": "password"
    }
}
```

## Example Response

Method: [getTaskResult](/api-docs/get-task-result)
API Endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
  "errorId": 0,
  "status": "ready",
  "solution": {
    "Domains": {
      "example.com": {
        "Cookies": {
          "TS386a400d029": "082670...01a06e",
          "TS386a400d078": "082670...dbb3b0c",
          "tspd_101_DID": "082670...1d53f"
        }
      }
    }
  }
}
```

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/vkcaptcha.svg" width="320" height="160" alt="VK captcha" />

<h1>VK captcha</h1>

</div>

We offer two methods to solve this type of captcha - token-based and image-based.

## Token-based method to bypass VK captcha

The VKCaptchaTask method requires `redirectUri` parameter, as well as proxy and userAgent. The value of the `redirectUri` parameter can be found in the response to requests to the VK API that return captchas.

> <b>Attention</b>, you must monitor the quality of the proxy used.

> <b>Attention</b>, you should provide your User-Agent that was used to interact with target website, it will be used to load and solve the captcha. Always use User-Agents of modern browsers.

## VKCaptchaTask task type specification

| Property         | Type      | Required | Description                                              |
| ---------------- | --------- | -------- | -------------------------------------------------------- |
| **type**         | *String*  | **Yes**  | Task type: <br>**VKCaptchaTask**                         |
| **redirectUri**  | *String*  | **Yes**  | The URL that is returned on requests to the captcha API.  |
| **userAgent**    | *String*  | **Yes**  | User-Agent of your browser will be used to load the captcha|
| **proxyType**    | *String*  | **Yes**  | Proxy type: <br>**http** <br> **https** <br> **socks5**  |
| **proxyAddress** | *String*  | **Yes**  | Proxy IP address or hostname                             |
| **proxyPort**    | *Integer* | **Yes**  | Proxy port                                               |
| proxyLogin       | *String*  | No       | Login for basic authentication on the proxy              |
| proxyPassword    | *String*  | No       | Password for basic authentication on the proxy           |


## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### VKCaptchaTask

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "VKCaptchaTask",
        "redirectUri": "https://id.vk.com/not_robot_captcha?domain=vk.com&session_token=eyJ....HGsc5B4LyvjA&variant=popup&blank=1",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": "8080",
        "proxyLogin": "user23",
        "proxyPassword": "p4$w0rd"        
    }
}
```
The query will return the ID of your captcha, which should be used to get the result.

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token":"eyJhbG...kyAWZSNoJPw"
    },
    "cost": "0.00145",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```
Use the token to interact with the target website.


## Image-based method to bypass VK captcha

- **VKCaptchaImageTask** - we use the `image` (image in base64 format) and `steps` parameters.
You can get both values from the response to the request https://api.vk.com/method/captchaNotRobot.getContent?v={API_VER} when loading the captcha widget on the page.

## VKCaptchaTask task type specification

| Property             | Type     | Required   | Description                                          |
| -------------------- | -------- | ---------- | ---------------------------------------------------- |
| **type**             | *String* | **Yes**    | Task type: <br>**VKCaptchaTask**                     |
| **image**            | *String* | **Yes**    | Image of the captcha task in base64 format           |
| **steps**            | *String* | **Yes**    | The value of the steps parameter from the response <br>to the request https://api.vk.com/method/captchaNotRobot.getContent?v={API_VER} when loading the captcha widget on the page |

## Request examples

Method: [createTask](/api-docs/create-task)
API endpoint: `https://api.2captcha.com/createTask`

### VKCaptchaImageTask

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type":"VKCaptchaImageTask",
        "image":"/9j/4AAQSkZJRg......",
        "steps":[5,19,14,14,6,4,8,9,23,23,14,23,3,13,16,8,2,4,6,16,1,1,3,12,23,18,12,24,17,7,6,22,2,4,0,22,3,18,11,5,4,5,6,14,22,21,6,10,0,3,14,18,19,2,24,0,3,23,9,21,5,24,21,0,4,15,14,21,8,5,17,19,12,19,15,17,21,11,8,4,15,0,18,16,19,4,19,20,21,22,16,10,20,12,19,5,23,24,8]
    }
}
```
The query will return the ID of your captcha, which should be used to get the result.

## Response example

Method: [getTaskResult](/api-docs/get-task-result)
API endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "best_step":46,
        "preview":"/9j/4AA......",
        "solution":[19,14,14,6,4,8,9,23,23,14,23,3,13,16,8,2,4,6,16,1,1,3,12,23,18,12,24,17,7,6,22,2,4,0,22,3,18,11,5,4,5,6,14,22,21,6,10,0,3,14,18,19,2,24,0,3,23,9,21,5,24,21,0,4,15,14,21,8,5,17,19,12,19,15,17,21,11,8,4,15,0,18,16,19,4,19,20,21,22,16,10,20],
        "answer":"eyJ2YW...yMF19"
    },
    "cost": "0.00145",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```
`best_step` - the number of steps you need to pass to solve the captcha, you can use this value to move the slider
`solution` - the list of steps passed to solve the captcha
`answer` - the `solution` in proper API format, use it to interact with the target website API
`preview` - is the base64 image showing the result of performing steps from the `solution`

---

# Callback (webhook)


We provide a callback (webhook) option that allows you to get the solution for your captcha automatically when it's ready.
It allows you to get answers without calling [`getTaskResult`](/api-docs/get-task-result) method and also allows you to avoid account suspension.

To receive automated callback you have to:

- Register your callback domain/IP address on [this page](/setting/pingback)
- Provide your callback URL as a value of `callbackUrl` parameter of your [`createTask`](/api-docs/create-task          )
  
Process incoming HTTP POST request with URLencoded form data (application/x-www-form-urlencoded) coming from our server to your callback URL. The request contains two parameters: id - captcha ID and code - the answer.
Incoming callback request example:

```
id=81555263943&code=ANSWER
```

You can use any callback URL pointing to your registered domain/IP address so your URL can include custom parameters.

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/yandex-smart-captcha.svg" width="320" height="160" alt="Yandex SmartCaptcha" />

<h1>Yandex SmartCaptcha</h1>

</div>

We offer two methods for solving Yandex SmartCaptcha in API v2: token-based and image coordinates.

> Use the `https://api.2captcha.com/createTask` endpoint to work with this method and get the result via `https://api.2captcha.com/getTaskResult`.

## Method specifications

- **YandexSmartCaptchaTaskProxyless** — solving using our proxies
- **YandexSmartCaptchaTask** — solving using your proxies
- **SmartCaptchaTask** — solving Smart Captcha by image, returning coordinates
- **PazlCaptchaTask** — solving Kaleidoscope (puzzle) captcha by image

---

## Token-based solving

### YandexSmartCaptchaTaskProxyless / YandexSmartCaptchaTask

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| **type** | *String* | **Yes** | Task type: `YandexSmartCaptchaTaskProxyless` or `YandexSmartCaptchaTask` |
| **websiteURL** | *String* | **Yes** | Full URL of the page where the captcha is loaded |
| **websiteKey** | *String* | **Yes** | The `sitekey` value from the page code or captcha iframe |
| userAgent | *String* | No | Your _userAgent_ to be used during solving |
| cookies | *String* | No | Cookies to send in the request, format: `name1=value1;name2=value2` |

### Proxy parameters (only for `YandexSmartCaptchaTask`)

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| **proxyType** | *String* | **Yes** | Proxy type: `http`, `https`, `socks4`, `socks5` |
| **proxyAddress** | *String* | **Yes** | IP address or hostname of the proxy server |
| **proxyPort** | *Number* | **Yes** | Proxy server port |
| proxyLogin | *String* | No | Login for proxy authorization |
| proxyPassword | *String* | No | Password for proxy authorization |

### Request example

Method: [createTask](/api-docs/create-task)  
Endpoint: `https://api.2captcha.com/createTask`

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "YandexSmartCaptchaTaskProxyless",
    "websiteURL": "https://mysite.com/",
    "websiteKey": "Y5Lh0ti..."
  }
}
```

### Response example

Method: [getTaskResult](/api-docs/get-task-result)  
Endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
  "errorId": 0,
  "status": "ready",
  "solution": {
    "token": "dV9xNjYyNTU3NjkxO4k9OTQuNVMuMjkuMjM9O9Q9MVEzQUEwMURERTY3RkUxQ9U3MTlEQzE3RjhYNTJCQUFFN9YyQTc3QUNFQjk9NzhVOTZGNjVCOEUyOVM4RTg9Q9VEQzY9NzY4O3U9MTY4MjU3NTY5MTQ4MTI3MVUyNVTo2ImVWMmQ4NWQzNjdlNzM9MVYhOGI5NWMxNWZlM4E4"
  }
}
```

> Use the received token in the `smart-token` field or pass it to the site backend similar to manual captcha solving.

---

## Image-based solving

> Suitable for visual Yandex SmartCaptcha tasks. Depending on the captcha variant, use `SmartCaptchaTask` (Smart Captcha) or `PazlCaptchaTask` (Kaleidoscope).

### Task specification: SmartCaptchaTask (Smart Captcha)

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| **type** | *String* | **Yes** | Task type: `SmartCaptchaTask` |
| **image** | *String* | **Yes** | Main captcha image in Base64 format, 320×180 |
| **imgInstructions** | *String* | **Yes** | Instruction image in Base64 format, 480×180 |
| comment | *String* | No* | Text hint for the worker. <br>* Recommended, e.g., `select objects in the order of the instruction` |

### Request example (SmartCaptchaTask)

Method: [createTask](/api-docs/create-task)  
Endpoint: `https://api.2captcha.com/createTask`

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "SmartCaptchaTask",
    "image": "BASE64_IMAGE",
    "imgInstructions": "BASE64_INSTRUCTION_IMAGE",
    "comment": "select objects in the order of the instruction"
  }
}
```

### Response example (SmartCaptchaTask)

Method: [getTaskResult](/api-docs/get-task-result)  
Endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
  "errorId": 0,
  "status": "ready",
  "solution": {
    "coordinates": [
      {"x": 57, "y": 82},
      {"x": 239, "y": 75},
      {"x": 138, "y": 113},
      {"x": 154, "y": 42},
      {"x": 230, "y": 155}
    ]
  }
}
```

> Always pass `imgInstructions` — without it, the worker may misunderstand the task. The `comment` parameter helps clarify the action order, especially if the instruction on the image is not obvious.

### Task specification: PazlCaptchaTask (Kaleidoscope)

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| **type** | *String* | **Yes** | Task type: `PazlCaptchaTask` |
| **image** | *String* | **Yes** | Main captcha image in Base64 format, 320×180 |
| **task** | *String* | **Yes** | Puzzle steps, as a JSON-stringified array (e.g. `"[15,24,4,13,10,...]"`) |

### Request example (PazlCaptchaTask)

Method: [createTask](/api-docs/create-task)  
Endpoint: `https://api.2captcha.com/createTask`

```json
{
  "clientKey": "YOUR_API_KEY",
  "task": {
    "type": "PazlCaptchaTask",
    "image": "BASE64_IMAGE",
    "task": "[15,24,4,13,10,...]"
  }
}
```

### Response example (PazlCaptchaTask)

Method: [getTaskResult](/api-docs/get-task-result)  
Endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
  "errorId": 0,
  "status": "ready",
  "solution": "8",
  "cost": "0.0012",
  "ip": "1.2.3.4",
  "createTime": 1692863536,
  "endTime": 1692863556,
  "solveCount": 1
}
```

`solution` is a string containing the number of clicks on the slider arrow needed to solve the captcha.

---

<div class="intro">

<img src="/assets/captcha-api-docs/img/yidun-necaptcha.svg" width="320" height="160" alt="Yidun" />

<h1>Yidun</h1>

</div>

A token-based method for bypassing Yidun NECaptcha.

## Task Types
- **YidunTaskProxyless** - we use our own proxy pool to solve captchas
- **YidunTask** - we use the proxy you provide

## Specification for YidunTaskProxyless Task Type

| Property                | Type      | Required | Description  |
| ----------------------- | -------- | ---------- | --------- |
| **type**                | *String* | **Yes**     | Task type: <br>**YidunTaskProxyless** <br> **YidunTask** |
| **websiteURL**          | *String* | **Yes**     | Full URL of the target web page where the captcha loads |
| **websiteKey**          | *String* | **Yes**     | Value of the `id` or `sitekey` parameter in the site's source code |
| userAgent               | *String* | No        | Browser User-Agent used to open the page |
| yidunGetLib             | *String* | No        | Full URL of the JavaScript file that loads the captcha. Recommended for Enterprise version |
| yidunApiServerSubdomain | *String* | No        | Yidun API server subdomain without the https:// prefix. Specify if using a custom server |
| challenge               | *String* | No        | Dynamic challenge parameter from network requests |
| hcg                     | *String* | No        | Captcha hash, used when forming the request |
| hct                     | *Number*  | No        | Numeric timestamp identifier for Enterprise version validation |

## Specification for YidunTask Task Type

The `YidunTask` task extends `YidunTaskProxyless`, adding a set of proxy-related parameters listed below.

| Property         | Type       | Required | Description                                                  |
| ---------------- | --------- | ---------- | --------------------------------------------------------- |
| **proxyType**    | *String*  | **Yes**     | Proxy type: <br>**http** <br> **socks4** <br> **socks5**  |
| **proxyAddress** | *String*  | **Yes**     | Proxy server IP address or hostname                     |
| **proxyPort**    | *Number*   | **Yes**     | Proxy server port                                       |
| proxyLogin       | *String*  | No        | Login for proxy server authentication                |
| proxyPassword    | *String*  | No        | Password for proxy server authentication               |

## Request Examples

Method: [createTask](/api-docs/create-task)
API Endpoint: `https://api.2captcha.com/createTask`

### YidunTaskProxyless Request Example

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "YidunTaskProxyless",
        "websiteURL": "https://example.com/page-with-yidun",
        "websiteKey": "0f743r3g1g...rz3grz0ym5",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
}
```

### Request Example with Enterprise Version Parameters

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "YidunTaskProxyless",
        "websiteURL": "https://example.com/page-with-yidun",
        "websiteKey": "0f743r3g1...rz3grz0ym5",
        "yidunGetLib": "https://example.com/yidun/load.min.js",
        "yidunApiServerSubdomain": "c.dun.163.com",
        "challenge": "0c59ba0da6e95...e3961a7b141fb1d",
        "hcg": "2c78a773...d7041f98228b28",
        "hct": 1779358333191
    }
}
```

### YidunTask Request Example with Proxy

```json
{
    "clientKey": "YOUR_API_KEY",
    "task": {
        "type": "YidunTask",
        "websiteURL": "https://example.com/page-with-yidun",
        "websiteKey": "0f743r3...0ym5",
        "proxyType": "http",
        "proxyAddress": "1.2.3.4",
        "proxyPort": 8080,
        "proxyLogin": "login",
        "proxyPassword": "password"
    }
}
```

## Response Example

Method: [getTaskResult](/api-docs/get-task-result)
API Endpoint: `https://api.2captcha.com/getTaskResult`

```json
{
    "errorId": 0,
    "status": "ready",
    "solution": {
        "token": "D19scz7n4VCU7b_...fRyEY-tXQ0cmS6laRKp_tZEyei_EUzc5M1IW0oxUHnZ4fBMH2a0jMPjOReiHVWBgkrcRYaOkQRasHlFejEToe7HZJy2jaGkxiB9b"
    },
    "cost": "0.003",
    "ip": "1.2.3.4",
    "createTime": 1692863536,
    "endTime": 1692863556,
    "solveCount": 1
}
```


### How to Find the Required Parameters

1. Open Developer Tools and go to the Network tab.
2. Trigger the captcha on the page.
3. Find a request that starts with `get?referer=` or `check?referer=`.
4. The `referer` value is your `websiteURL`. If it's encoded, decode it first.
5. The `id` value in that request is your `websiteKey`.
6. If you see `challenge`, `hcg`, or `hct` parameters in requests like `cscPreprocess?reflushCode=`, you're dealing with the Enterprise version. Include these in your task along with `yidunGetLib` and `yidunApiServerSubdomain`.

Tip: The `challenge`, `hcg`, and `hct` parameters change dynamically. Pull them right before you submit your task, or the solution might not work.