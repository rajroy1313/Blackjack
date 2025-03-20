import discord
import random
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Player money storage
player_money = {}
DEFAULT_BALANCE = 1000  # Starting money

# Card values for Blackjack
def card_value(card):
    if card in ['J', 'Q', 'K']:
        return 10
    elif card == 'A':
        return 11  # Ace is counted as 11 initially
    else:
        return int(card)

def calculate_hand(hand):
    total = sum(card_value(card) for card in hand)
    aces = hand.count('A')
    while total > 21 and aces:
        total -= 10  # Convert Ace from 11 to 1
        aces -= 1
    return total

# Game class for Blackjack
class Blackjack:
    def __init__(self, bet):
        self.deck = [str(i) for i in range(2, 11)] + ['J', 'Q', 'K', 'A'] * 4
        random.shuffle(self.deck)
        self.player_hand = [self.deck.pop(), self.deck.pop()]
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        self.game_over = False
        self.bet = bet
    
    def hit(self, hand):
        hand.append(self.deck.pop())
    
    def dealer_turn(self):
        while calculate_hand(self.dealer_hand) < 17:
            self.hit(self.dealer_hand)
    
    def game_result(self):
        player_total = calculate_hand(self.player_hand)
        dealer_total = calculate_hand(self.dealer_hand)
        if player_total > 21:
            return "You busted! Dealer wins.", -self.bet
        elif dealer_total > 21 or player_total > dealer_total:
            return "You win!", self.bet
        elif player_total < dealer_total:
            return "Dealer wins!", -self.bet
        else:
            return "It's a tie!", 0
    
    def reset(self, bet):
        self.__init__(bet)

game = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def balance(ctx):
    user = str(ctx.author.id)
    balance = player_money.get(user, DEFAULT_BALANCE)
    await ctx.send(f"{ctx.author.mention}, your balance is: ${balance}")

@bot.command()
async def start(ctx, bet: int):
    global game
    user = str(ctx.author.id)
    player_money[user] = player_money.get(user, DEFAULT_BALANCE)
    
    if bet > player_money[user] or bet <= 0:
        await ctx.send(f"{ctx.author.mention}, you don't have enough money or invalid bet amount!")
        return
    
    player_money[user] -= bet
    game = Blackjack(bet)
    await ctx.send(f"Blackjack started!
Your bet: ${bet}
Your hand: {game.player_hand} (Total: {calculate_hand(game.player_hand)})
Dealer shows: {game.dealer_hand[0]}")

@bot.command()
async def hit(ctx):
    global game
    if not game or game.game_over:
        await ctx.send("Game is over! Use !start to play again.")
        return
    
    game.hit(game.player_hand)
    total = calculate_hand(game.player_hand)
    if total > 21:
        game.game_over = True
        await ctx.send(f"You drew a card. Your hand: {game.player_hand} (Total: {total})\nYou busted! Dealer wins.")
    else:
        await ctx.send(f"You drew a card. Your hand: {game.player_hand} (Total: {total})")

@bot.command()
async def stand(ctx):
    global game
    if not game or game.game_over:
        await ctx.send("Game is over! Use !start to play again.")
        return
    
    game.dealer_turn()
    game.game_over = True
    result, money_change = game.game_result()
    user = str(ctx.author.id)
    player_money[user] += money_change
    await ctx.send(f"Dealer's hand: {game.dealer_hand} (Total: {calculate_hand(game.dealer_hand)})\n{result}\nYour new balance: ${player_money[user]}")

bot.run('YOUR_BOT_TOKEN')
