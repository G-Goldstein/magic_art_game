# magic_art_game
Play the Magic art game in Slack

To use, you'll need to create a magic_art_game.settings file in the same directory as the code, containing this JSON object:

	{
		"default_difficulty":<One of the Magic Art game difficulties, such as "easy" or "impossible">,
		"magic_channel_url":<The URL of your incoming Slack hook. Ask me for details>,
		"magic_channel_name":<Your channel name>,
		"magic_bot_name":<A name for your Bot to post as>,
		"magic_bot_icon":<An icon for the bot. Here's a good one: https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Magic_the_gathering_pentagon.png/220px-Magic_the_gathering_pentagon.png>,
		"cards_in_game":10,
		"time_for_answers":20,
		"time_between_cards":10
	}

Run art_game.py to start it, specifying the difficulty and a True/False value for whether to post to Slack.
