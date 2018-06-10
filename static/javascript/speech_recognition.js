function log() {
  console.log('_Y_', arguments);
}

function YQ_SpeechRecognition (video_command_cbs, status_change_cb) {
  if(!annyang) {
    return;
  }

  var self = this;
  self._video_cmd_callbacks = video_command_cbs;
  self._status_change_cb = status_change_cb;

  self._enable_debug = function(c) {
    log('Enabling SpeechRecognition Debug');
    annyang.debug();
  }

  self._disable_debug = function(c) {
    log('Disable SpeechRecognition Debug');
    annyang.debug(false);
  }

  self._stop_listen = function(c) {
    log('Stop SpeechRecognition');
    annyang.abort();
  }

  self._restart_video = function(c) {
    log('Restart Video');
    if (self._video_cmd_callbacks.hasOwnProperty('restart')) {
      self._video_cmd_callbacks['restart']();
    }
  }

  self._play_video = function(c) {
    log('Play Video');
    if (self._video_cmd_callbacks.hasOwnProperty('play')) {
      self._video_cmd_callbacks['play']();
    }
  }

  self._pause_video = function(c) {
    log('Pause Video');
    if (self._video_cmd_callbacks.hasOwnProperty('pause')) {
      self._video_cmd_callbacks['pause']();
    }
  }

  self._end_video = function(c) {
    log('End Video');
    if (self._video_cmd_callbacks.hasOwnProperty('end')) {
      self._video_cmd_callbacks['end']();
    }
  }

  self._skip_video = function(c) {
    log('Skip Video');
    if (self._video_cmd_callbacks.hasOwnProperty('skip')) {
      self._video_cmd_callbacks['skip']();
    }
  }

  var speech_commands = {
    'debug': self._enable_debug,
    'debug off': self._disable_debug,
    'stop speech': self._stop_listen,
  };

  var video_commands = {
    'restart': self._restart_video,
    'stop': self._pause_video,
    'pause': self._pause_video,
    'play': self._play_video,
    'end': self._end_video,
    'skip': self._skip_video,
  };

  // annyang.debug();
  annyang.setLanguage('en-US');
  annyang.addCommands(speech_commands);
  annyang.addCommands(video_commands);
  if (self._status_change_cb) {
    annyang.addCallback('start', function() {self._status_change_cb('start')});
    annyang.addCallback('error', function() {self._status_change_cb('error')});
    annyang.addCallback('end', function() {self._status_change_cb('end')});
  }

  self.start = function(){
    log('YQ_SpeechRecognition Starting');
    annyang.start();
  }

  self.stop = function(){
    annyang.abort();
  }

  self.isListening = function(){
    return annyang.isListening();
  }
}
