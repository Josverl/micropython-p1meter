

## todo
- [ ] add actionable descriptions to common errors
- [ ] switch to more stable MQTT lib
- [ ] more robust network reconnection 
- [ ] test / repro network disconnect - re-connect 
- [ ] clear last sent sate on network / mqtt reconnect

- [ ] periodically send all readings ( per minute / hour ? configurable)
- [ ] logging formatting with colors 
  [?] add queue of messages to send 

### Done
- [x] catch more MQTT errors
- [x] replace codes -> topic names 
- [x] simulator:  support larger messages 
- [x] only save updated if send actually succeded, to avoid dampening/removing unsent changes / states  

## Dev setup 
 - git clone
 - micropy install

Prereqs : 
 - git client
 - python 3.x installed 
recomended: 
 - vscode
 - pymakr extention
 - pip install micropy-cli 


