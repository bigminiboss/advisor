from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from IPython.display import display, Image, Audio

import threading
import pyautogui
import cv2
import numpy as np
import time
import os
import base64
import openai
import markdown2
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# Globals for screen recording
screen_width, screen_height = pyautogui.size()
fourcc = cv2.VideoWriter_fourcc(*'XVID')
frame_rate = 30
out = None
is_recording = False
recording_thread = None
output_file = "screen_recording.avi"

@csrf_exempt
def home(request):
    return render(request, "home.html")

def record_screen():
    """Function to record the screen in a separate thread."""
    global out, is_recording
    while is_recording:
        frame = capture_screen()
        out.write(frame)
        # time.sleep(1)
    if out:
        out.release()

def capture_screen():
    """Capture the current screen and return it as a NumPy array."""
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame

@csrf_exempt
def start_recording(request):
    """Start screen recording in a separate thread."""
    global out, is_recording, recording_thread
    if is_recording:
        return JsonResponse({"error": "Recording already in progress."}, status=400)
    is_recording = True
    out = cv2.VideoWriter(output_file, fourcc, frame_rate, (screen_width, screen_height))
    recording_thread = threading.Thread(target=record_screen, daemon=True)
    recording_thread.start()
    return render(request, "start_recording.html")

@csrf_exempt
def stop_recording(request):
    """Stop screen recording."""
    global is_recording
    if not is_recording:
        return JsonResponse({"error": "No recording in progress."}, status=400)
    is_recording = False
    recording_thread.join()  # Wait for the thread to finish
    return render(request, "stop_recording.html")

@csrf_exempt
def analyze_gameplay(request):
    """Analyze gameplay from the recorded video."""
    if not os.path.exists(output_file):
        return JsonResponse({"error": "No recording found to analyze."}, status=400)
    
    video = cv2.VideoCapture(output_file)
    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
    video.release()
    print(len(base64Frames))

    # Prompt for OpenAI
    background_info = """ this is background information on the topic of 1.8.9 pvp
# 🗝️Key
* Low Ping refers to the ping range 0-60 ms
* Medium-Low ping refers to the ping range 60-90 ms
* Medium ping refers to the ping range 90-120 ms
* Medium-High Ping refers to 120-170 ms
* High Ping refers to 170+ ms
* **1️⃣** | **Beginner:** A technique that can be perfected after `20 minutes` of dedicated practice and thoughtful studying. 
* **`2️⃣` | Intermediate:** A technique that can be perfected after `1-3 hours` of dedicated practice and thoughtful studying. 
* **`3️⃣` | Advanced:** A technique that can be perfected after `5-10 hours` of dedicated practice and thoughtful studying. 
* **`4️⃣` | Expert:** A technique that can be perfected after `20+ hours` of dedicated practice and thoughtful studying, normally a **combination of multiple lower level techniques** and possibly some adjacent Advanced techniques. 
* **`5️⃣` | Peak:** Techniques coming from someone with well over `100 hours` of thoughtful practice that were **created out of their intuition**. Not attainable or really teachable except for with practice.
# Sprint Reseting/Spacing
A very important aspect of minecraft 1.8.9 and even just minecraft pvp in general is sprint reseting, briefly sprint reseting is when you briefly "reset your sprint" between hits. This works because in minecraft each hit affter the initial sprinted hit deals reduced knockback asymptotically to 0. You can do it in between hits because minecraft has a invincibility frame which lasts for 1 tick and is a frame where you are unable to deal any kb to the opponent although you can override his previously taken damage. There are other spacing methods like 7tapping where you quickly tap a and d to reduce your movement speed to about 4 m/s isntead of the normal 5.6 m/s but this doesn't reset your sprint so you will inevitibally get too close to the opponent and jump comboing where you spam click on the opponent while sprint jumping and this slows you down and resets your sprint
## > W tapping nons
W tapping is the most widely used and generally effective form of sprint reseting, to preform it, you hold w until you hit your opponent and then let go (I will discuss other timings of W tapping but this is the most common one called offensive W tapping). I recommend that you learn to light w tap which is where you space it in such a manner that you are only pressing w for the split second in which you are hitting your opponent as most players nowadays are using some sort of cheat/have high ms and must be comboed in this manner. To practice, you can try a bot pvp server like esta.land, pvp.land, or practice against friends/random q. This is the best method of sprint resetting as it perfectly combo holds without having to do extra steps. 

### >> Defensive W taps 
To defensive w tap, you w tap immediately after you have been hit, this causes a similar effect to how if you are breaking an object with a tool in one slot but then switch to another, minecraft will not start breaking the block until way after you switched. Similarly, you will not start your forward movement again after you are hit until significantly later unless you reinput the forward movement into minecraft.
### >> Zest Tapping
Zest tapping is a hypixel specific sprint reset technique. Since hypixel has a relatively odd form of kb administration in which the first two hits tend to deal a reasonable amount of kb but the third hit deals an incredibly large amount. To combat this, you can preform this technique in which you hold w for two hits while strafing one direction and then when the opponent begins to fall, let go of w and hit them without it and then press w again. Rinse and repeat, [this](https://www.youtube.com/watch?v=Dfj1oHBOKwQ) is a great video by asian batman where he goes more indepth but because sprint reseting is not the crux of this guide I will not be giving a full length explanation
## > Block Hitting
A block hit is a sprint reset where you block your sword in between hits, this allows you to sometimes get a blocked hit, reducing damage. similar to w taps.
## > S tapping
this sprint reset method involves letting go of W, and tapping s, generally to INCREASE not MAINTAIN spacing, for example, if you started a combo at 2 blocks you would s tap 1 or 2 hits in order to make the combo 2.5-2.7 blocks, or when fighting a cheater or high ms player

---
# How CPS affects PVP
often a misunderstood component of PVP, CPS affects by allowing you to take less kb. The way it works is that minecraft generally runs at around 20 ticks per second, and minecraft will detect the amount of times you click on an entity. Now, importantly, it can only detect one click per tick, meaning that if you click 3 times in one tick minecraft will only register it as one click and not give you kb reduction of 3 clicks but 1. Because it runs at 20 ticks per second, minecraft will approximately count your clicks every 50 ms or 0.05 seconds, which is slighly above the standard time that a glorious mouse can be set to debounce. Interestingly, if you butterfly click and most of the clicks come from double clicks that are spaced at 0-4 ms, this will result in NO extra kb reduction. This is why there is often an insane gap between 20 cps from a butterflying and 20 cps from a perfectly spaced autoclick and why you often need to be dragging and insane cps in order to garuntee that you are hitting the 20 clicks per tick limit legimately for minecraft.

---
# How Ping affects PVP
Another often misunderstood aspect of minecraft is how ping affects PVP, often terms like high, low, and medium ping get thrown around with vague mentions of why a certain one is better or what the pros and cons are of each ping. However, in top fight especially, a very important ping to be concerned about is cumulative ping. Because of this, if two players are moving towards each other while sprinting, the true position of each character is the same because the server receives each client movement packet and then sends it to the other client, but the respective movements are both delayed. Meaning that if the delay from the client 1 to the server is 20 ms, and then the delay for the server to send this information to client 2 is 200 ms, then it will be a total 220 ms delay and vice versa. Importantly, the reason that 20 ms players hits register first even though the clients both receive the ability to hit each other at the same time is because the server receives the packet of the 20 ms player before the 200 ms player and thus registers is first. However, the opponent at 200 ms will hit 200 ms later but ALSO take knockback 200 ms later, which is why it is so hard to combo a high ping player. Because of the fact that ping is cumulative and hits only register after the cumulative delay, this gives less of a trade advantage than is often made out to. However, there is still an important advantage that higher ping players have over lower ping players. This is that they take the knockback later than the opponent, this allows them to move forward more and counteract more of the knockback dealt to them. Now, I will briefly discuss movement speed in minecraft, which is 5.6 blocks per second while sprinting and sprint jumping is 7.1 b/s. The 200 ms player is significantly more displaced than the 20 ms player because of the higher ping. This is why a high ping player going very fast often gives the illusion of more reach especially in comboes; because the delay is so high, either player holding a combo will give a much greater distance due to high cumulative ping. 

![[Pasted image 20241021105335.png]]
If an opponent's movement vector is canceled out, then they are going to have their true positions more equal to their server positions (obviouisly they can take backwards kb but this vector is always smaller than than the forwards vector in magnitude). Thus, whoever has more momentum's true position will be farther from their cumulative server position. This will increase the reach of the person with more momentum as they are able to move more forward and thus increase the gap between their true and server position. This is why stopping someone's momentum fully via projectiles like rods or blocks will allow for a "free" combo since you have increased movement and thus more reach. Reach means that the distance in between the displaced visual position and "true"-er position of the comboed player is larger, not that the server's stored positions of each player ever violates the reach rules

---
# How Momentum and Reach Vectors affect PVP
Having higher momentum will significantly reduce your knockback even outside of high ping, the reason is that when you get hit and kb is administered, then minecraft will deal you a constant k of knockback, if you had higher momentum, then you will have your momentum, *m* - *k* be larger than if you were moving slower. Importantly, there are two components to kb, when you are hit minecraft administers and additional upwards and backwards kb to your players which is eventually counteracted by your movement forward and gravity which pulls you towards the ground.

Reach vectors in minecraft are important, a relatively well known bit of trivia is that in minecraft to maximize reach you should aim as straight as possible as the vector for hitting comes around eye level of your character and is 3 blocks long. Importantly though, the hitbox of a player is always a perfectly rectangular prism. This means that when going at an angle, you should aim more towards the point closest towards you to also maximize reach
![[Pasted image 20241021110832.png]]

---
# Hitdelays
When you hitdelay another player, you are manipulating the **hitsequence** or the order in which hits are administered to each player. Preforming it correctly allows you to control the amount of knockback administered to yourself and the opponent. When you delay your hit, you are countering more knockback allowing yourself to conserve more momentum and also giving yourself the low ground. The reason is that if you delay your hit until later, then they will also take knockback up and backwards but because your hit was after, they also start falling after. With low ground, you actually increase your reach slightly due to the fact that you are able to hit their hitbox while their reach vector is higher
![[Pasted image 20241021113627.png]]
## > Invincibility frames
when you get hit, there is a small delay after which you can get hit again (500 ms). This is an example with midtrading
![[Pasted image 20241021141946.png]]

## > Light Hitdelays

a light hitdelay is the safest hitdelay because it is delaying very very little, this is preformed by waiting 1 or 2 ticks (100 ms) after your opponent hits you and then hitting them back (that is, hitting them while you are still taking kb upwards and not even falling yet). Unless the opponent has perfect three block reach and you are both playing at incredibly low cumulative ms, then you can safely preform this technique essientally everytime. This works especially well against low ms flawless players when the cumulative ms is around 100-140 because they will attempt a flawless at close to 3 blocks and because they take pretty much immediate kb you can abuse your higher ping to take delayed kb and then also hit them so they fall right outside hitting distance and get a combo 
### >> High Ping Hitdelay
an even lighter version of this technique is used when your cumulative ping is very high (around 250 ms) and thus abusing the server latency allows you to correctly space your hit by just starting to click on the opponent the moment they hit you. notice that this is the hitdelay is the exact same as the previously mentioned light hitdelay due to adding server latency.

## > Normal Hitdelays
a normal hitdelay is a delay right as you start falling (300 ms), this is the most widely known version of hitdelays but is significantly more prone to getting flawlessed because the delay is slightly out of the complete safety zone if the cumulative ping is low enough. This is most famous as it is easiest to follow into a combo given that you successfully do it as you are pretty much already given a reach advantage the moment you start hitting.
## > Long Hitdelays
a long hitdelay is delaying your hit for around 470-490 ms. which is delaying your hit until right before your invincibility frame ends. This method is extremely risky as you need to have high momentum in order to not get flawlessed and extremely precise timing in order to not get comboed from long hitdelaying.

## > Hitselects (First Hit Hitdelays)
A hitselect is preformed at the beginning of a hitsequence in order to ideally immediately start a combo
![[Pasted image 20241021113217.png]]
Again, your are manipulating the hitsequence in order to gain more reach over the opponent via low ground, take less kb and thus increase reach due to server delatency, etc. However, it is still possible to win a trade against terrible players by hitselecting the first hit and spam clicking because of the initial small advantage of reach and hitsequence manipulation.
### >> Amplified Hitselects
An amplified hitselect is when you let go of w when you are hit and then press it again afterwards, this effectively kills most of your momentum and administers more knockback; here you are manipulating the spacing so that you fall farther outside the range of the opponent.

## > Hit Select Counters
### >> Hardstrafing
a technique used to counter a hitselector is to hardstrafe. That is, strafing in a single direction. This forces a hitselector to hit you lest they mess their aim up right before you move out of their sight range. This allows you to basically hitselect them instead. After they hit you, generally abusing 100+ personal and 150+ ms cumulative ping to be able to essientally tank the hit and use your momentum and delayed kb to only take the kb so that it doesnt push you back into their line of sight and then combo them. Also called potion selecting.
![[Pasted image 20241022223158.png]]
#### >> S tapping
For someone who is normal to long hitselecting a great counter is s tapping. This doesnt work against a light hitselector as they are not hitselecting for long enough that holding s will allow you to move out of range but it works relatively well against long hitselectors as they are waiting an extremely long time and are not really moving forward as their momentum is canceled. The best way to s tap is to hardstrafe to one side with a finger on a or d (ring or pointer finger) and then your middle finger on the w key and the othjer finger not pressing a or d hovering over s to be prepared for the s tap
### >> Counter Strafing
A counter strafe is a method of abusing the the outer corner of the hitbox while strafing in order to hit the edge of the hitbox. This works well even against someone who is not hitselecting. This method is preformed by strafing in the "harder" in a certain direction until you are able to hit the edge of the hitbox as previously explained unless the person is also intentionally counterstrafing and aiming for this effect, it allows you to hit the very edge of the hitbox and preform a flawless. A great tip to preform this is to strafe in one direction and then switch to fake them to one side or to spam a and d and hope you hit them on the edge of the hitbox. This method works best at lower pings as your hit will register earlier 
### >> Pre Hit W tap
this method is preformed by letting go of w and hitting the opponent who is hitselecting and hitting them while you are letting go of w and then when they hitselect start holding w again. This allows you to reap the benefits of the hitselect instead of them because you administer less kb. Because of this, you will go pretty much perfectly out of the combo right before your invincibility frame is over forcing the opponent to other uselessly hit you or to be unable to hit you because of your invincibility frame and giving you the low ground. Now importantly, someone can fake a hitselect out on you and then start spam clicking right before they are in range and effectively render you not holding w into a combo so it's very much about timing and the timing of the tap is quite important
## > Midtrading
Midtrading is essientally manipulating a hitsequence within a trade. If you've even hitselected and been annoyed that the opponent basically takes out your advantage through high cps, this is how to counter it, it is delaying your hits in a manner every single hit. When trading, the main idea is to manipulate the trade so that at the end of the trade you have the low ground. This is often achieved by reducing your momentum by **light hitdelaying** every hit in a trade and w tapping defensively (immediately after you get hit). This will reduce your knockback the most and also conserve the most momentum and velocity; generally, this leads to winning a trade. 

However, remember that the part of the trade where you reap the benefits of the trade is at the end but that the middle is the part where you set yourself up for success and are actually actively manipulating the hitsequence. I categorize trades into three distinct phases at the high level
1. the 0-1 block trade, or close trading
2. the 1.1-2 block trade, or midtrading
3. th 2.1-2.5 block trade, or endtrading
### >> Close trading
When you are close trading, it is essiental to understand you do not want to stay in this trade for very long especially on top fight where health is involved. You want to move out of this trade fairly quickly and move onto midtrading which is where the hitsequence manipulation occurs. Unless you are both trading at perfect 20 clicks per ticks then you will move out of this trade quickly. Alternatively, there are some playstyles which abuse close trading in order to long/normal delay or black trade and phase through the opponent for a free combo. 
### >> Mid trading
When you are at 2 blocks, this is where most of the hitsequence manipulation occurs. Often simply light hitdelaying the opponent is sufficient to come out on top of a trade. However, against a good player you should mix in some long hitdelays and black trading, which is when you wait until you are on the ground to hit the opponent this allows you to control the hitsequence as they are waiting for you to hit them so you force the trade to be reset by touching the floor again. Importantly, black trading should **only** be done when the opponent is also a midtrader in order to "regain" control of the hitsequence even if they are waiting to hit you after you hit them. Otherwise, this method will almost always result in getting comboed by someone who is just spam clicking. Another interesting way to midtrade is remember how I said that you w tapping the moment you get hit administers the least kb because you are immediately telling minecraft that you would like to start going forward again? Well, you can manipulate this to be slightly later at around the apex of your kb (so right before you would normal hitdelay) and then w tap this will cause you to take a different type of kb. Importantly, kb is not always about taking less but about manipulating it; in this case you do it so that you take way less as you fall but that you did go up so that you counteract the falling process. This results in an hitsequence pattern where you are both taking turns going up and down but your falling timing is significantly shorter
### >> End Trading
when you are trading at the end of a hitsequence make sure to only light hitdelay/spam click as although you may have manipulated the sequence to retain more momentum you still do not have quiet enough to long hitselect or even normal hitselect at 2.1-2.5 blocks.
## > Phase Selecting

Phase selecting is a method that especially abuses high (100+ personal ping and 200+ ms cumulative ping) in order to delay the kb from a close range hit and use extra momentum to effectively counteract it so much that you just go through the opponent and mess their aim up leading to a free combo

# Trapping (An Overall Strat and Hitselect Counter)
Trapping is an overall strat but also a very interesting hitselect counter, this is done by first hitting and works best against hitselectors, the reason is because you generally dont want to preform it at 2.7 blocks because someone maay end up accidentally or purposefully light hitselecting you, you want to preform it on a hitselector (that is someone who is intenitionally awaiting your hit) at around 2 blocks and ideally click quiet high cps to reduce. Then, you wait for their hit. And then their next hit. The reason this works is that they expect you to hit them back  and initiate a hitsequence which they initially manipulated to be in their favor so they start hitting you; however, you hitdelay THEM and manipulate the hitsequence from that point onwards in YOUR favor

---
# Jump Reseting
Jump reseting is when you press jump at the same time as you receieve a hit, minecraft will mistake this as upward kb so that you take the upward kb of the hit and also the kb that was supposed to be dealt to you backwards which is now converted the reason this seems like it is less kb is because gravity in minecraft is simply higher than every other acting force outside of high speed a player can achieve so the vector gets canceled out faster. Now this technique should not be spammed. A good player can mess you up, force trade you, etc. You should generally only jump reset on every other hit starting with the second hit.

---
# Playstyles
Common playstyles. Importantly, these are general playbooks but are not set in stone if you find yourself in an opportunity even if it doesn't fit your ping range you can go for it (for example, dewier is actually quite good at longselecting despite being low ping he just knows how to use it)

## > Hitselect Spammers
hitselect pretty much every hit and if possible initiate close walk throughs to mess up the aim of the opponent this works well against higher ping players because their pvp relies almost entirely on messing up YOUR aim. Try to long hitselect every fight opening (importantly ensure you have momentum). This requires good aim, ideally you want to be 80-150 ms because this will allow you to hitselect easier. This playstyle is relatively easily countered via s tapping and counterstrafing of a low ping player it is a relatively risky method 
* ping: 80-150
* examples: qbedwars when playing casually, levetche
## > Midtrading
A midtrader abuses first hits to trap opponents in trades and then trys to lead into a trade in which they manipulate the hitsequence with a variety of light, normal, and long hitdelays (the ordering of which depends on your ping and whatnot and your experience with them)
* ping 60-100 ms
* largely effective against everything because you are not allowing yourself to get flawlessed and also initiating a trade which you are manipulating do note this method should be utilized with higher ish clicks per 20 ticks
* examples: most ranked sumo players
## > First Hitters
counterstrafe, s tap, abuse higherh momentum, etc. anything to get first hit and hold a combo. Works well against *long selectors* but gets countered pretty easily by someone midtrading
* ping: 0-40 ms
* examples: dewier, kobsters
    """
    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                background_info + "These are frames from gameplay of the video game minecraft specifically on the server minemen.club on 1.8.9 (the combat version without hitdelay) please provide insightful commentary as to what the player did right and what they did wrong",
                *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::5]),
            ],
        },
    ]
    params = {
        "model": "gpt-4o",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 500,
    }

    try:
        result = client.chat.completions.create(**params)
        print(result.choices[0].message.content)
        return render(request, "analyze_gameplay.html", {"analysis": markdown2.markdown(result.choices[0].message.content)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
