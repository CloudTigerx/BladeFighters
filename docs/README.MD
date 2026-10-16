BLADE FIGHTERS!
python3 -m swordfighting_new.pygame_client
We should aim for a modular architecture to make easier adjustments

similar game list for quick context, THIS IS NOT TETRIS OR A MATCH 3 TYPE GAME

PUYO PUYO
PUZZLE PIRATES SWORD FIGHTING
CRYSTAL CRISIS

TECH WE ARE WORKING WITH, MACBOOK PRO 48GB MEMORY, WINDOWS PC 4080 SUPER FOR CUDA AI IMAGE GENERATION + CHATGPT IMAGE GENERATION, I9 INTEL 13900K CPU, 32 GB DDR5 MEMORY - GOOD SET UP
---------------
LIBRARIES - PYGAME, ?, ?, ?
---------------
The game client should adapt to the native resolution of the device, even if scaling is enabled on the device for Mac and Windows
hopefully this game can be expanded into the mobile industry, iphone, and android
---------------
GRID SYSTEM
6 WIDE 12 HIGH 
The grid has edges, top, and bottom; pieces cannot penetrate these areas. The grid and puzzle board visuals should align
---------------
ORDER OF COLUMNS LEFT TO RIGHT 0,2,3,4,5,
---------------
order of rows bottom to top 0,1,2,3,4,5,6,7,8,9,10,11
---------------
PIECE SPAWNS OUT OF COLUMN 4, ABOVE THE PUZZLE, VISIBILITY UPON ENTRY INTO THE GRID
piece sizes and board sizes need to be discussed, we have a temp board and i can resize our current pieces -
---------------
breakers spawn with pieces at a 1/4 chance, breakers are able to break same color blocks
-------------
PIECES AND BREAKERS SPAWN TOGETHER VERTICALLY OUT OF THE 4RTH COLUMN FROM ABOVE THE BOARD, 2 TOTAL PIECES SPAWN ATTATCHED PER PIECE
NEXT PIECE SPAWNS AFTER PIECE LANDS

ALL PLAYERS RECEIVE THE SAME PIECES IN REGARDS TO PIECES SPAWNING

PIECE PREVIEW FOR THE NEXT PIECE OUTSIDE OF PUZZLE GRID, TOP LEFT RIGHT OUTSIDE OF GRID
-------------
PIECE COLORS RED, BLUE, GREEN, YELLOW
breaker colors - red,blue,yellow,green
ASSETS blueblock.png yellowblock.png redblock.png greenblock.png
ASSETS bluebreaker.png yellowbreaker.png redbreaker.png greenbreaker.png
ASSETS purple_scarlet1.png 384x 960x
---------------
Gravity has global effects on pieces, breakers, blocks above broken blocks, sprinkle attacks, CLUSTERS, AND SWORD STRIKES, there is nothing gravity does not have effects on except the bottom of the board.
---------------
WE USED MICROGRID MOVEMENT IN THE PAST - IF WE CAN IMPROVE TO SOMETHING BETTER LETS DO IT
-----------
PIECE SPEED (gravity measurement) = 
SPACE BAR ACCELERATES PIECE (gravity mutiplier on actual puzzle piece, nothing else) =
-------------------
CONTROLS LEFT, RIGHT, UP, DOWN, SPACE BAR

piece movement important/ easily to be confused - down rotates the top piece clockwise around the bottom piece, up rotates the piece counterclockwise around the top piece. essentially 
---------------
if piece is falling horizontally and lands on uneven columns; gravity applies to piece with empty grid cells below
--------------
if a piece is between two columns, it can still flip up/down -- if piece is on the grid walls and up/down is pressed the piece essentially kicks off the wall into the next column unless column has piece then piece will just flip up/down - wallflip mechanic
------------
clusters are any block formations of the same color size two wide, two high or higher examples
[COLUMN WIDTH ALWAYS FIRST X ROW WIDTH ALWAYS SECOND]
EVERY POSSIBLE CLUSTER SIZE
2x2,2x3,2x4,2x5,2x6,2x7,2x8,2x9,2x10,2x11,2x12
3x2 3x3 3x4 3x5 3x6 3x7 3x8 3x9 3x10 3x11 3x12
4x2,4x2,4x4,4x5,4x6,4x7,4x8,4x9,4x10,4x11,4x12
5x2,5x3,5x4,5x5,5x6,5x7,5x8,5x9,5x10,5x11,5x12
6x2,6x3,6x4,6x5,6x6,6x7,6x8,6x9,6x10,6x11,6x12
clusters should glow when formed, need to discuss assets vs rendering effects/libs
clusters have been difficult in previous attempts of creating bladefighters, consider dedicated detection..?
-------------
COMBO SYSTEM
no cap limit on possible combos
breakers destroy pieces, gravity causes pieces to fall into empty grids, this can trigger more breakers to destroy matching color pieces
welcome to puzzle fighting - 
1x combo, 2x combo, 3x combo, no cap
player builds pieces, stacking carefully
destroys pieces, pieces fall onto same color breakers 2x combo init, gravity applies - should be same gravity speed all around except space bar effect on pieces traveling through the grid, once breaking init space bar should have no effect until piece spawns again, space bar should be pressed everytime new piece spawns to accelerate BUT should be a setting in options in the future along with common puzzle game movement features
DAS (Delayed Auto-Shift): the initial delay after you hold the key before auto-repeat kicks in.
ARR (Auto-Repeat Rate): the speed at which the piece keeps moving once auto-shift is active.
should be included in settings + hard drop - but we will turn it off in the beginning but i assume its best practice to code it before we realize we forgot it
----------
SETTINGS MUST INCLUDE ABILITY TO CHANGE CONTROLS
---------
top of board behavior should allow player to easily manipulate pieces into positions 1x13, pieces should not improperly vanish - pieces spawn as 2 pieces, if column/rows 1,2,3,5,6 row 11 is full and pieces are placed here, after final piece lock/set - the bottom piece is in play and can function, the top piece nulls, top piece has no action, no effect on boards, does not fall to gravity even if pieces bellow break - it is gone. 
---------
pieces should break cascading if that's the correct terminology. However, clusters break as one piece. blocks out of clusters are called sprinkle. if sprinkle is break, start break at point of contact, point of contact spreads simontanously to same color blocks, they break, spread to next same color blocks
cascade breaking accounts for up, down, left, right, but not diagnal 
---------

ATTACK SYSTEM

Sprinkle Calculations

If the attack is a combo, the formula is applied to each individual step in the combo, and the results are summed up. 
The formula is the number of blocks in that group (each breaker also counts as one block) divided by 2 and then floored, then multiplied by the combo size.
The example I will use will be to single 3 blocks, double 4 blocks, and triple 5 blocks. When the attack is separated into each individual combo-step then you'll have a group of 3(Single), 4(Double), and 5(Triple). Now you must divide the number of blocks in each group by two. The 3 is now 1.5, the 4 becomes 2, and the 5 is 2.5. You then floor each of the results. This simply means that for any group that has half a block, just remove the .5. The 1.5 is now 1, 2 will stay 2, and 2.5 becomes 2. For the final step, just multiply each group by it's respective combo size and add the numbers together to get the total amount of sprinkles sent. 1 singled is 1, 2 doubled is 4, and 2 tripled is 6. 1 + 4 + 6 = 11. Therefore, this particular attack would send 11 sprinkles.

Sprinkle Placement

The side in which sprinkle attacks start on also goes back and forth 
(right, left, right, left, right, left... etc)

visual flow (assuming 6 columns numbered 1-6):
Right attack: 6 → 1 → 5 → 2 → 3 → 4
Left attack: 1 → 6 → 2 → 5 → 3 → 4
Why this works well:
✅ Both patterns end at column 4 (maximum protection)
✅ Starts from the designated side (right=6, left=1)
✅ Alternates between sides before hitting center
✅ Players can memorize the pattern for strategic planning
✅ Creates interesting decisions about where to build defenses
For your design doc, you can describe it as:
> "Sprinkles follow an edge-to-center pattern starting from the attack side, with column 4 always receiving sprinkles last to prevent easy instakills."
This gives you consistent, learnable behavior while maintaining the strategic depth of your instakill protection system.
The first sprinkle of the game always lands on the right. Note that also like swords, both opponent's drops count towards the side the sprinkle will fall on. (eg. You send a sprinkle and it will fall on the right, opponent sends a sprinkle it will land on your left, then you send another sprinkle it will land on the right again.) The difference between the back and forth mechanism between swords and sprinkles is that each sword sent is assigned either left or right handed switching back and forth. However, not each sprinkle sent is assigned to fall on the left or the right, but instead the entire attack (All of the sprinkles sent over in the same turn) is assigned to be either a left side or right side attack.
If the sprinkle is supposed to start on the right side, it drops a block, moves to the left and drops, moves to the left and drops and so on. If it starts from the left side, it does the exact same except it drops then moves to the right.
Sprinkle Wastage
Sprinkles attempt to fall evenly across the board. If a column is already entirely filled to the top, the sprinkles will still act as if they landed in that column. They will not move to another open column to maximize the number of sprinkles that actually land on the opponent's screen.
Sprinkle Instakill
Finally, sprinkles cannot land any higher in column 4 than 10 rows up. This makes it impossible to actually instakill someone with sprinkles. If column 4 on the opponent's screen is already filled 10 rows high, the sprinkles will act the same as they would if it was a different column that was entirely filled to the top. This means they too will not move to land in another open column, they will just be wasted.

How Vertical Swords Are Created

First we'll explain how vertical swords are created. When you build a gem that is taller than it is wide, it creates a vertical sword. Also, if you break a gem that is equal in both height and width it will send a vertical sword. All vertical sword's lengths are greater than their width. This is why there are no square vertical swords that hit your opponent. 2x2 gems singled become 1x4 swords and 3x3 gems singled become 2x4 swords. The maximum width a sword can be is 3 blocks wide. If a gem is built wider than 3 spaces, you subtract 1 block from it's width and add it to it's length. Eg. A 4x5 block becomes a 3x6 sword. When you combo a gem you multiply the swords length by the size of the combo. Doubling a 2x3 gem creates a 2x6 sword. Back to the first example of if you double a 4x5 gem, first the gem becomes a 3x6 gem and then doubled become a 3x12 sword.

If you break a gem that is wider than it is tall it creates a horizontal sword. Horizontal swords are explained in the horizontal placement section found further below. However, there are special cases where a horizontal sword will turn into a vertical sword. If at least half of a horizontal sword cannot enter into the opponent's screen, then the horizontal sword will turn into a vertical sword of the same length. This will be described in greater detail in the appropriate horizontal section.

The Underlying Mechanisms

There are two basic mechanisms underlying sword placement. Two underlying queues for all swords dropped on the screen. Both queues are shared between opponents. Both in 1vs1 and multiplayer brawls. This means that not only do your opponents get the same pieces as you, their swords also count as a turn in the sword pattern explained below.
First: Each sword follows a successive order across the screen, starting in column 2.

2, 3, 4, 5, 6, 1

Second: Swords alternate right handed, and left handed.

R, L, R, L, R, L

Right handed meaning if they're horizontal they come in from the right side of the screen. Or if they're vertical, when they're blocked by either another sword or a 'gem', they move right of the obstacle until it finds a place it can land. Left handed meaning the opposite. Namely that a left handed horizontal will come in from the left, and vertical it will move left through the pattern to avoid obstacles (avoiding obstacles will be described in greater detail below).

Vertical Sword Placement Rules

Not only is vertical sword placement based on those two underlying mechanisms, it also follows 6 main rules explained below that help guide when and where a sword can land in certain situations.

1. How Swords Avoid Obstacles

As hinted earlier, swords may sometimes be unable to land in the desired column because an obstacle is present. Obstacles may include other swords, gems on the opponent's screen, or the 4th column which swords attempt to avoid. The solution is that a sword will try to move to the left or to the right to find another column that it can successfully land in.
The concept is easy to understand. If the sword is a 'right-handed' sword, it will first attempt to move right one column and check if it can land there. If it can't land there, then it will move one more column to the right and repeat the process. If it is a 'left-handed' sword then it will begin checking to the left to find an available column to drop in. If a 'right-handed' sword checks every column to the right and is still unable to find a column to drop in, then it will begin checking to the left. The same goes for 'left-handed' swords but with reversed directions.

2. Swords Falling on Top of Each Other

Vertical swords can never fall on top of another vertical sword. If a sword is going to fall on top of another sword, it will move over across the screen either left or right depending on whether it's a right or left handed sword. After it finds a place to land, the next swords will fall just as they would if the other sword didn't have to be moved, except now maybe they too will be landing on top of a sword and may also have to be moved.

3. Swords Forced to Land In a Column

Vertical swords cannot land in column 4 unless there is no other open spaces the sword can drop in, and the sword can fit into the space where part of it or all of it lands in column 4. (eg. A 2xN in column 1/2 and a 2xN in column 5/6 with one more 2xN still having to land. The last 2xN can only fit in column 3/4, so that's where it drops. 3xN's can be forced to land in column 4 if another sword sent at the same time lands completely in column 1,2, and/or 3. No matter what, part of the sword would have to land in column 4.

4. Solid Blocks at the Very Top of the Screen

If there is any solid block at the very top of the screen (top of gem in row 13) where the sword should land, and the sword is completely blocked from entering the screen at all, it will move left or right to avoid the obstacle based on whether it's a right or left handed sword.

5. Solid Blocks Stopping Full Sword From Landing

Individual swords also try to maximize the damage they deal. If there is a gem on the opponent's screen where the sword intends to land that prevents the entire sword from falling, it will begin looking for a column where the whole sword can enter the screen. If the sword finds that it cannot land anywhere on the screen completely, it searches through the pattern until it finds the place where the largest amount of the sword can fit on the screen. However, the sword will not land with any part of it in column 4 unless it has no other possible place to go. (See rule 3 for this case)

The example I will use is having a 2x2 built on the very bottom of the defending screen in columns 3 and 4. The attacker then sends a sword 12 rows tall that is intended to land in column 2/3. Should the sword land in column 2/3 it would fall partially on the 2x2 and be stopped 2 rows up allowing only only 11 rows of the full 12 to enter the screen. In order to maximize your attack, the sword is then forced to move left or right until it can completely land on the defending screen. In this case, if it were the first sword of the game, the vertical sword would move through the pattern to an empty column 5/6 where it can fit fully on the screen and drop there.

6. Wasted Swords

There are a number of situations in the swordfighting puzzle where 'wastage' will occur. Wastage can happen two ways. The first way is partial wastage. This occurs any time a vertical or horizontal sword cannot entirely enter the opponent's screen. Any part of the sword that cannot fit onto the screen will simply disappear and be 'wasted'. The second way is full wastage. This occurs when a sword has absolutely no where to land, as defined by the previous given sword rules. Because the sword is unable to enter the opponent's screen in any row or column, it will also just disappear and be 'wasted'. It will not hit the opponent at a later turn when it would be possible for it to enter the screen.

The Sword Drop Patterns

There is an individual drop pattern for each size of vertical sword. These patterns vary in length depending on the width of the sword. It is important to remember that sending any sword will advance the index one spot forward for all of the patterns.
Below you will see two drop sequences for each size of sword. The first sequence is the theoretical order which is where the sword would land if it wasn't bound by any of the other 5 vertical placement laws described above. However, when the sword falls it is bound to adhere the vertical placement laws. Specifically this means that the swords must avoid falling in column 4. The second sequence you will see is what the actual result will be when the sword avoids column 4.

An asterisk (*) will be used to signify when a sword moved out of order to avoid column 4.
1x4 Pattern
1x4s will drop in the following order
Column:
2, 3, 4, 5, 6, 1 (theoretical order)
2, 3, 5*, 5, 6, 1, repeated... (actual result avoiding column 4)
The third sword will always be a right handed sword, so it will always avoid column 4 by moving to the right into column 5.
2xN Pattern
2xNs will drop in the following order
Column:
2/3 3/4 4/5 5/6 1/2 2/3 3/4 4/5 5/6 1/2 (theoretical order)
2/3 2/3* 5/6* 5/6 1/2 2/3 5/6* 2/3* 5/6 1/2, repeated... (actual result avoiding column 4)
The second sword is a left handed sword, so it avoids dropping 3/4 by moving to the left to 2/3. The third sword is a right handed sword, and avoids dropping 4/5 by moving to the right to 5/6. Sword seven is a right handed sword, and avoids dropping 3/4 by moving to the right to 5/6. Sword eight is a left handed sword, and avoids dropping in 4/5 by moving to the left to 2/3.
3xN Pattern
3xNs will drop in the following order
2/3/4 3/4/5 4/5/6 1/2/3 (theoretical order)
1/2/3* 1/2/3* 1/2/3* 1/2/3, repeated... (actual result avoiding column 4)
I realize that a single 3xN can only drop in 1/2/3 to avoid column 4, but bear with me as I explain what is happening behind the scenes.
Sword one is a right handed sword but it cannot land anywhere to the right without dropping in column 4, so it then keeps moving left until it lands in 1/2/3. Sword two is a left handed sword and moves left through the order to 1/2/3. Sword three is a right handed sword but again cannot land to the right without dropping in column 4, so it too then keeps going left until it lands in 1/2/3.
Combos
Combos do not affect the order of swords in the queue.
As each successive sword in the combo breaks, it is inserted into the next spot of both the column placement queue, and the handedness queue.
That is to say, for example; In a triple, any sword generated by the first breaker broken will be inserted first into the queue, followed by any sword generated by the second breaker, followed by any sword generated by the third breaker.
Horizontal Swords

How Horizontal Swords Are Created
First we'll explain how horizontal swords are created. If the attacking player builds a gem on their screen that is wider than it is tall, it creates a horizontal sword. Because horizontal swords enter from the side we define it's length by how far it enters into the screen and it's width as how many rows it hits. Horizontal swords are a minimum of 2 blocks wide a maximum of 3 blocks wide. If a horizontal gem is more than 3 rows tall, you subtract 1 block from the horizontal width and add 1 block to it's length. Eg. A 6x4 gem becomes a 7x3 horizontal.
Just like vertical swords, you multiply a horizontal sword's length by the size of a combo. A 3x2 gem doubled becomes a 6x2 horizontal sword. If we go back to the first example and double the 6x4 gem, first the gem becomes a 7x3 and then doubled becomes a 14x3. As you know the swordfighting board is only 6 blocks wide, therefore the maximum length a horizontal sword can enter into the screen is 6 spaces regardless of it's actual length. However, horizontal swords are affected by one notable rule. As rule 3 of the horizontal placement laws describes below, if at least half of a horizontal sword cannot enter the screen it will become a vertical sword. This means that any horizontal sword that reaches a length of 12 blocks will automatically turn into a vertical sword because the screen is only 6 blocks wide. It is important to note that while horizontal swords can turn into vertical ones, vertical swords will never change into horizontal swords for any reason.
Horizontal Placement Rules
Just as vertical swords are subject to 6 main vertical sword placement laws, there are 3 horizontal placement laws that will affect where a horizontal will enter the opponent's screen.
1. No Gems on Opponent's Screen
If there are no 'gems' (2x2's, 2x3's, ...etc.. solid blocks) on your opponent's screen, it is based on how high the highest block on the defending person's screen is, the turn right before the horizontal enters the screen. The top of the horizontal will enter 2 rows below the highest piece on the defending screen.
2. Gems on Opponent's Screen
However, if there is a 'gem' (solid block) on the defending screen, the horizontal changes so that the top of the horizontal lands 3 rows below the bottom of the very lowest gem.
3. Horizontals Turned Vertical
As mentioned above, there are some situations where horizontal swords will actually turn into vertical swords. This will happen when at least half of the horizontal sword cannot enter the screen unimpeded. This is why all horizontal swords that reach a length of 12 will automatically turn into vertical swords because they can only enter the screen a maximum of 6 spaces in from the sides. Gems on the opponent's screen can also affect this. For example, if column's 5 and 6 on the opponent's board were entirely filled with a solid gem, any horizontal sword of at least 8 blocks long would turn vertical because at maximum it could only enter 4 spaces into the screen (meaning at least half of the horizontal sword would not be able to enter the screen).
In other odd cases a horizontal sword may be unable to enter the opponent's screen from either sides of their board. An example of this would be having 2 gems screen-high on both sides of the opponent board. As you know, horizontals cannot go through gems therefore the sword cannot possibly enter the screen horizontally. If this happens, the horizontal sword turns vertical. It should also be noted that in absolutely no cases can a horizontal sword enter in row 13. If the only possible place a sword could enter the screen is partially in column 13 then the sword will be forced vertical.

Horizontal Entrance Tables
Note for the patterns including 'gems', the horizontal may be forced to move up or down depending on whether or not something is in the way, for example... a 2x2 in row 1/2 on the far right would just make the horizontal switch sides, however 2 2x2's on both sides will force the horizontal to move up.
Height1	Rows (No gems)	Rows (With gems)
2 wide	3 wide	2 wide	3 wide
1-4	1/2	1/2/3	1/2	1/2/3
5	2/3	1/2/3	1/2	1/2/3
6	3/4	2/3/4	2/3	1/2/3
7	4/5	3/4/5	3/4	2/3/4
8	5/6	4/5/6	4/5	3/4/5
9	6/7	5/6/7	5/6	4/5/6
10	7/8	6/7/8	6/7	5/6/7
11	8/9	7/8/9	7/8	6/7/8
12	9/10	8/9/10	8/9	7/8/9
13	1/2	1/2/3	N/A2	N/A2
1 A height of X refers to row X, or X blocks up from the bottom. If there are no gems, the height is the row number of the highest block on the defending player's screen. If there are gems, the height is the row number of the bottom of the lowest gem on the defending player's screen. Once again, the game checks this the turn before the horizontal enters the screen.
2 It is impossible to have the bottom of the gem in row 13, hence the N/A.
Which Side the Horizontal Enters From
Horizontals enter from the side of the screen based on whether it's a right or left handed sword. If it's right handed it enters from the right side, and if it's left handed it enters from the left. If a horizontal is the very first sword of the game sent, it will enter on the right.
Therefore, if the number of swords you have sent is even, horizontals should enter from the right, and if it's odd they should enter from the left. This is unless there is a 'gem' or another horizontal or vertical sword in the way. In this case it switches sides and checks if it can enter at the same height from the opposite direction. This will not change the back and forth pattern though, so if it has to switch sides from hitting the right side to hitting the left side, the next horizontal will still hit the left side again as it would if the first horizontal had been allowed to enter on the right. If there is a 'gem(s)' stopping it from entering at that height on both sides, it checks back and forth ( right - left ... in order based on which side it was originally supposed to enter), then drops down another level and again checks both sides. If it cannot enter the screen any lower, it goes higher then it was originally supposed to hit in the same manner checking back and forth, but going up 1 row each time instead of going down. You can block a horizontal from entering at all or fully entering by completing a 'gem' in it's path on the turn where you see the horizontal flashing at the side.
Two Horizontals Entering From the Same Side
If you manage to send two horizontals that should enter from the same side, and the first horizontal lands high enough up that the second horizontal can enter below it, then the second horizontal acts like the first horizontal is a gem. If in fact that 'new gem' is the lowest gem on the screen, it will land 3 rows beneath it just as it would if there really was a gem there.
Horizontals Count as a Turn in the Pattern
As stated above, horizontals also count as one of the turns in the vertical sword pattern. So if you send a horizontal very first it would make the first 1x4 sent over, the second sword sent, go into column 3, the second number in the pattern. Also, looking back on an old forum thread I saw that someone had posted that horizontals always land before vertical swords, so I thought I should clear this up. This is untrue, horizontal swords do not always land before vertical swords. All swords enter the screen in the same order that they are broken in on the attacking side. This includes horizontal and vertical swords, this is why sometimes a vertical sword will enter first and the horizontal will crash into its side, and sometime the horizontal will hit first and the vertical will fall on top of it.
Horizontal Instakill
It is impossible to instakill using only a horizontal sword. This means a horizontal will never hit so high up that the top of the horizontal is in row 13. It is possible for it to land in row 12 and below, but in order for part of a horizontal to hit in either row 11 or 12 it would have to have been forced to move up.
------------------
--- SWORDS ARE NOT INDIVIDUAL BLOCKS, THEY ARE ESSENTIALLY CLUSTERS MASKED WITH A SWORD DESIGN, FOR EXAMPLE LAST GAME ATTEMPT STRIKES WERE SENT AS SPRINKLE GROUPS INSTEAD OF AN ACTUAL OBJECT
-------------------
WHEN SPRINKLE IS RECIEVED, PIECE SPAWN IS TRUE, IF PIECE IS PLACED, SPRINKLES TRANSFORM INTO COLOREDGARBAGE, WHEN NEXT PIECE IS SET, COLORED GARBAGE TURNS INTO NORMAL PIECES

ASSETS - REDGARBAGE.PNG, BLUEGARBAGE.PNG, YELLOWGARBAGE.PNG, GREENGARBAGE.PNG - I NEED TO RENAME THESE
---------
WHEN STRIKES ARE RECIEVED IT FOLLOWS SIMILAR PROCESS, INCOMING PAYLOAD, PIECE SPAWN FALSE, PAYLOAD DELIVER, PIECE SPAWN TRUE, PIECE PLACE, STRIKE TURNS INTO SPRINKLE, UPON NEXT PIECE PLACE, SPRINKLE TURNS INTO COLORED GARBAGE, UPON NEXT PIECE PLACE COLORED GARBAGE TURNS INTO NORMAL BLOCKS.

Game Over Conditions

What happens when pieces can't spawn? (column 4 blocked?)
LAST PIECE IS SET, PIECE CAN BREAK IF ABLE, GRAVITY APPLIES, IF NEXT PIECE SPAWN WILL HIT THAT PIECE - GAME OVER

Is there a "danger zone" above row 12?
IF GAME OVER CONDITION DOES NOT ANSWER THIS QUESTION LET ME KNOW AND ELABORATE, IF IT DOES ANSWER THIS QUESTION LET ME KNOW

Multiplayer: first to die loses, or time-based?
PVP, FIRST TO DIE LOSES, WE SHOULD CONSIDER OTHER GAME MODES TOO!

2. Win Conditions
ANSWERED FOR STANDARD GAME MODE

Tournament format considerations?
YES, LATER

3. Piece Movement Timing
How fast do pieces fall normally?
1600 MS FROM TOP SPAWN TO ROW 0 SET/LOCK

Space bar acceleration multiplier?
NEED TO ADJUST MYSELF TO GET CORRECT *

Lock delay (time before piece locks when it hits bottom)?
YES BUT IT IS MINIMAL, HARD TO PUT A SECURE NUMBER ON

4. Input System Details
DAS/ARR values you mentioned but didn't specify
ALSO A GOOD QUESTION, ALSO WE ONLY WANT THIS FEATURE FOR LEFT/RIGHT MOVEMENT NOT SPACE BAR REPEATING

Rotation priority (can you rotate while moving?)
YES

5. Cluster vs Sprinkle Breaking
You defined clusters (2x2+) but when do they break vs individual blocks?
SAME BREAKING CONCEPT AS SPRINKLE, SAME COLOR MATCHING BREAKER WILL BREAK CLUSTER AS A WHOLE PIECE - THEN CASCADES ACCORDINGLY TO ALL SAME COLOR BLOCKS TOUCHING IT

6. Attack Timing
When do sprinkles/swords actually land? (immediately after combo? delayed?)

ATTACKS ARE ASSOCIATED WITH THE PIECE THAT BROKE IT - IF IM FASTER THAN THE ENEMY AND I SEND ATTACKS QUICK, THEY WILL HAVE TO CATCH UP TO THAT BLOCK THAT SENT THE ATTACK TO RECIEVE IT. IF BOTH PLAYERS ARE THE SAME SPEED THEN ATTACKS ARE SENT AT THE SAME TURN - 

Can you defend against incoming attacks?
THIS IS SOMETHING TO BE EXPERIMENTED WITH, LIKE ATTACKS CANCELING EACHOTHER OUT
BUT ORIGIONALLY NO

7. Multiplayer Synchronization
How do "same pieces for all players" work with timing?
Network lag handling?
Spectator mode?

ELABORATE IF NOT ANSWERED
PLAYERS RECIEVE THE SAME PIECE SPAWNS, I SUPPOSE A BATCH CAN BE GENERATED AT GAME START, THEN IF REACH CERTAIN AMOUNT GENERATE MORE
THEY HAVE TO BE RANDOMIZED BUT EACH PLAYER NEEDS THE PIECES AS THE OTHER PLAYER FOR FAIRNESS
CANT BLAME THE PIECES FOR LOSING/ BOTH PLAYERS HAD SAME PLAYING FIELD

Still Need Numbers:
Space bar acceleration multiplier: You said "NEED TO ADJUST MYSELF TO GET CORRECT " - what's your target? (2x speed? 4x speed?)
4x
DAS/ARR values: You want it for left/right only - what feels right? (DAS: 150ms delay? ARR: 50ms repeat?)
50ms repeat left/right only
Lock delay: You said "minimal" - is it 0ms (instant) or ~100ms?
50ms
Multiplayer Sync (needs elaboration):
Piece timing: If I'm faster and place 10 pieces while you place 5, do we desync? Or does the game wait for both players to place before advancing the shared piece queue?
DESYNC IS FINE AS LONG AS WHEN I WOULD CATCH UP I STILL RECIEVE THE SAME PIECES YOU DID - GENERALLY IF YOURE FASTER THEN IM PROBABLY GOING TO LOSE WHENEVER THE ATTACKS CATCH UP -

Attack delivery: You said attacks are "associated with the piece that broke it" - does this mean if I'm 3 pieces ahead, my attack won't hit you until you catch up to that same piece number?
now that i think about this, i always hated that mechanic, it did not make sense because if they are really that slow you are just beating a dead horse but; this means newer players could just get crapped on without ever gaining experience in getting a chance to play... i feel like a 4 turn delay between attack sending and recieving would probably be easier to implement, is a little simpler, and easy for everyone to grasp. what do you think

Your game over answer is perfect ✅ - spawn collision = game over, no danger zone needed.
One clarification on clusters:

 clusters break "as a whole piece - then cascades accordingly to all same color blocks touching it."
this means:
Breaker touches cluster → entire cluster disappears instantly → cascade spreads from where cluster was
-------
theres a mechanic im thinking of, its the one you asked me about last chance before piece is placed 50ms - i think this mechanic also satisfies the mechanic i notice when placing a breaker on a piece, theres a tiny delay before that break initiates. 
----------
STRIKE MAPPING
STRIKE MAPPING (1-indexed rows, row 12 = top of board)

SQUARE CLUSTERS (Equal width/height):
2x2 * 1 = 1x4,  2x2 * 2 = 1x8,  2x2 * 3 = 1x12
3x3 * 1 = 2x4,  3x3 * 2 = 2x8,  3x3 * 3 = 2x12
4x4 * 1 = 3x5,  4x4 * 2 = 3x10, 4x4 * 3 = 3x12
5x5 * 1 = 3x6,  5x5 * 2 = 3x12
6x6 * 1 = 3x7,  6x6 * 2 = 3x12

VERTICAL CLUSTERS (Taller than wide):
2x3 * 1 = 1x4,  2x3 * 2 = 1x6,  2x3 * 3 = 1x9,  2x3 * 4 = 1x12
2x4 * 1 = 1x5,  2x4 * 2 = 1x8,  2x4 * 3 = 1x12
2x5 * 1 = 1x6,  2x5 * 2 = 1x10, 2x5 * 3 = 1x12
2x6 * 1 = 1x7,  2x6 * 2 = 1x12
2x7 * 1 = 1x8,  2x7 * 2 = 1x12
2x8 * 1 = 1x9,  2x8 * 2 = 1x12
2x9 * 1 = 1x10, 2x9 * 2 = 1x12
2x10 * 1 = 1x11, 2x10 * 2 = 1x12
2x11 * 1 = 1x12
2x12 * 1 = 1x12

3x4 * 1 = 2x5,  3x4 * 2 = 2x8,  3x4 * 3 = 2x12
3x5 * 1 = 2x6,  3x5 * 2 = 2x10, 3x5 * 3 = 2x12
3x6 * 1 = 2x7,  3x6 * 2 = 2x12
3x7 * 1 = 2x8,  3x7 * 2 = 2x12
3x8 * 1 = 2x9,  3x8 * 2 = 2x12
3x9 * 1 = 2x10, 3x9 * 2 = 2x12
3x10 * 1 = 2x11, 3x10 * 2 = 2x12
3x11 * 1 = 2x12
3x12 * 1 = 2x12

4x5 * 1 = 3x6,  4x5 * 2 = 3x10, 4x5 * 3 = 3x12
4x6 * 1 = 3x7,  4x6 * 2 = 3x12
4x7 * 1 = 3x8,  4x7 * 2 = 3x12
4x8 * 1 = 3x9,  4x8 * 2 = 3x12
4x9 * 1 = 3x10, 4x9 * 2 = 3x12
4x10 * 1 = 3x11, 4x10 * 2 = 3x12
4x11 * 1 = 3x12
4x12 * 1 = 3x12

5x6 * 1 = 3x7,  5x6 * 2 = 3x12
5x7 * 1 = 3x8,  5x7 * 2 = 3x12
5x8 * 1 = 3x9,  5x8 * 2 = 3x12
5x9 * 1 = 3x10, 5x9 * 2 = 3x12
5x10 * 1 = 3x11, 5x10 * 2 = 3x12
5x11 * 1 = 3x12
5x12 * 1 = 3x12

6x7 * 1 = 3x8,  6x7 * 2 = 3x12
6x8 * 1 = 3x9,  6x8 * 2 = 3x12
6x9 * 1 = 3x10, 6x9 * 2 = 3x12
6x10 * 1 = 3x11, 6x10 * 2 = 3x12
6x11 * 1 = 3x12
6x12 * 1 = 3x12

HORIZONTAL CLUSTERS (Wider than tall):
3x2 * 1 = 3x2,  3x2 * 2 = 6x2,  3x2 * 3 = 9x2,  3x2 * 4 = 12x2→1x12
4x2 * 1 = 3x3,  4x2 * 2 = 6x3,  4x2 * 3 = 9x3,  4x2 * 4 = 12x3→1x12
5x2 * 1 = 3x4,  5x2 * 2 = 6x4→1x12, 5x2 * 3 = 9x4→1x12
6x2 * 1 = 3x5,  6x2 * 2 = 6x5→1x12, 6x2 * 3 = 9x5→1x12

4x3 * 1 = 3x4,  4x3 * 2 = 6x4→1x12, 4x3 * 3 = 9x4→1x12
5x3 * 1 = 3x5,  5x3 * 2 = 6x5→1x12, 5x3 * 3 = 9x5→1x12
6x3 * 1 = 3x6,  6x3 * 2 = 6x6→1x12, 6x3 * 3 = 9x6→1x12

Note: → indicates horizontal sword converts to vertical due to length ≥12
----------
strikes can pierce non clustered blocks and sprinkle

----------
strikes and sprinkles as one payload
3x7 * 1 = 2x8,  3x7 * 2 = 2x14→2x12, 3x7 * 3 = 2x21→2x12, 3x7 * 4 = 2x28→2x12, 3x7 * 5 = 2x35→2x12
3x8 * 1 = 2x9,  3x8 * 2 = 2x16→2x12, 3x8 * 3 = 2x24→2x12, 3x8 * 4 = 2x32→2x12, 3x8 * 5 = 2x40→2x12
3x9 * 1 = 2x10, 3x9 * 2 = 2x18→2x12, 3x9 * 3 = 2x27→2x12, 3x9 * 4 = 2x36→2x12, 3x9 * 5 = 2x45→2x12
3x10 * 1 = 2x11, 3x10 * 2 = 2x20→2x12, 3x10 * 3 = 2x30→2x12, 3x10 * 4 = 2x40→2x12, 3x10 * 5 = 2x50→2x12
3x11 * 1 = 2x12, 3x11 * 2 = 2x22→2x12, 3x11 * 3 = 2x33→2x12, 3x11 * 4 = 2x44→2x12, 3x11 * 5 = 2x55→2x12


4x5 * 1 = 3x6,  4x5 * 2 = 3x10, 4x5 * 3 = 3x15→3x12, 4x5 * 4 = 3x20→3x12, 4x5 * 5 = 3x25→3x12
4x6 * 1 = 3x7,  4x6 * 2 = 3x12, 4x6 * 3 = 3x18→3x12, 4x6 * 4 = 3x24→3x12, 4x6 * 5 = 3x30→3x12
4x7 * 1 = 3x8,  4x7 * 2 = 3x14→3x12, 4x7 * 3 = 3x21→3x12, 4x7 * 4 = 3x28→3x12, 4x7 * 5 = 3x35→3x12
4x8 * 1 = 3x9,  4x8 * 2 = 3x16→3x12, 4x8 * 3 = 3x24→3x12, 4x8 * 4 = 3x32→3x12, 4x8 * 5 = 3x40→3x12
4x9 * 1 = 3x10, 4x9 * 2 = 3x18→3x12, 4x9 * 3 = 3x27→3x12, 4x9 * 4 = 3x36→3x12, 4x9 * 5 = 3x45→3x12
4x10 * 1 = 3x11, 4x10 * 2 = 3x20→3x12, 4x10 * 3 = 3x30→3x12, 4x10 * 4 = 3x40→3x12, 4x10 * 5 = 3x50→3x12
4x11 * 1 = 3x12, 4x11 * 2 = 3x22→3x12, 4x11 * 3 = 3x33→3x12, 4x11 * 4 = 3x44→3x12, 4x11 * 5 = 3x55→3x12

5x6 * 1 = 3x7,  5x6 * 2 = 3x12, 5x6 * 3 = 3x18→3x12, 5x6 * 4 = 3x24→3x12, 5x6 * 5 = 3x30→3x12
5x7 * 1 = 3x8,  5x7 * 2 = 3x14→3x12, 5x7 * 3 = 3x21→3x12, 5x7 * 4 = 3x28→3x12, 5x7 * 5 = 3x35→3x12
5x8 * 1 = 3x9,  5x8 * 2 = 3x16→3x12, 5x8 * 3 = 3x24→3x12, 5x8 * 4 = 3x32→3x12, 5x8 * 5 = 3x40→3x12
5x9 * 1 = 3x10, 5x9 * 2 = 3x18→3x12, 5x9 * 3 = 3x27→3x12, 5x9 * 4 = 3x36→3x12, 5x9 * 5 = 3x45→3x12
5x10 * 1 = 3x11, 5x10 * 2 = 3x20→3x12, 5x10 * 3 = 3x30→3x12, 5x10 * 4 = 3x40→3x12, 5x10 * 5 = 3x50→3x12
5x11 * 1 = 3x12, 5x11 * 2 = 3x22→3x12, 5x11 * 3 = 3x33→3x12, 5x11 * 4 = 3x44→3x12, 5x11 * 5 = 3x55→3x12

6x7 * 1 = 3x8,  6x7 * 2 = 3x14→3x12, 6x7 * 3 = 3x21→3x12, 6x7 * 4 = 3x28→3x12, 6x7 * 5 = 3x35→3x12
6x8 * 1 = 3x9,  6x8 * 2 = 3x16→3x12, 6x8 * 3 = 3x24→3x12, 6x8 * 4 = 3x32→3x12, 6x8 * 5 = 3x40→3x12
6x9 * 1 = 3x10, 6x9 * 2 = 3x18→3x12, 6x9 * 3 = 3x27→3x12, 6x9 * 4 = 3x36→3x12, 6x9 * 5 = 3x45→3x12
6x10 * 1 = 3x11, 6x10 * 2 = 3x20→3x12, 6x10 * 3 = 3x30→3x12, 6x10 * 4 = 3x40→3x12, 6x10 * 5 = 3x50→3x12
6x11 * 1 = 3x12, 6x11 * 2 = 3x22→3x12, 6x11 * 3 = 3x33→3x12, 6x11 * 4 = 3x44→3x12, 6x11 * 5 = 3x55→3x12

HORIZONTAL SWORDS (Wider than tall clusters):
3x2 * 1 = 3x2,  3x2 * 2 = 6x2,  3x2 * 3 = 9x2,  3x2 * 4 = 12x2→1x12, 3x2 * 5 = 15x2→1x12
4x2 * 1 = 3x3,  4x2 * 2 = 6x3,  4x2 * 3 = 9x3,  4x2 * 4 = 12x3→1x12, 4x2 * 5 = 15x3→1x12
5x2 * 1 = 3x4,  5x2 * 2 = 6x4→1x12, 5x2 * 3 = 9x4→1x12, 5x2 * 4 = 12x4→1x12, 5x2 * 5 = 15x4→1x12
6x2 * 1 = 3x5,  6x2 * 2 = 6x5→1x12, 6x2 * 3 = 9x5→1x12, 6x2 * 4 = 12x5→1x12, 6x2 * 5 = 15x5→1x12

4x3 * 1 = 3x4,  4x3 * 2 = 6x4→1x12, 4x3 * 3 = 9x4→1x12, 4x3 * 4 = 12x4→1x12, 4x3 * 5 = 15x4→1x12
5x3 * 1 = 3x5,  5x3 * 2 = 6x5→1x12, 5x3 * 3 = 9x5→1x12, 5x3 * 4 = 12x5→1x12, 5x3 * 5 = 15x5→1x12
6x3 * 1 = 3x6,  6x3 * 2 = 6x6→1x12, 6x3 * 3 = 9x6→1x12, 6x3 * 4 = 12x6→1x12, 6x3 * 5 = 15x6→1x12

SQUARE CLUSTERS (Equal width/height):
2x2 * 1 = 1x4,  2x2 * 2 = 1x8,  2x2 * 3 = 1x12, 2x2 * 4 = 1x16→1x12, 2x2 * 5 = 1x20→1x12
3x3 * 1 = 2x4,  3x3 * 2 = 2x8,  3x3 * 3 = 2x12, 3x3 * 4 = 2x16→2x12, 3x3 * 5 = 2x20→2x12
4x4 * 1 = 3x5,  4x4 * 2 = 3x8,  4x4 * 3 = 3x12, 4x4 * 4 = 3x16→3x12, 4x4 * 5 = 3x20→3x12
5x5 * 1 = 3x6,  5x5 * 2 = 3x10, 5x5 * 3 = 3x15→3x12, 5x5 * 4 = 3x20→3x12, 5x5 * 5 = 3x25→3x12
6x6 * 1 = 3x7,  6x6 * 2 = 3x12, 6x6 * 3 = 3x18→3x12, 6x6 * 4 = 3x24→3x12, 6x6 * 5 = 3x30→3x12
