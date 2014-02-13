/*
  ==============================================================================

    This file was auto-generated!

    It contains the basic startup code for a Juce application.

  ==============================================================================
*/

#include "PluginProcessor.h"
#include "PluginEditor.h"

const float defaultGain = 1.0f;
const float defaultDelay = 0.0f;
const int nyquist = 44100;

//==============================================================================
_1f_ilterAudioProcessor::_1f_ilterAudioProcessor()
: delayBuffer (2, 5)
{
    // Set up some default values..
    gain = defaultGain;
    delay = defaultDelay;
}

_1f_ilterAudioProcessor::~_1f_ilterAudioProcessor()
{
}

//==============================================================================
const String _1f_ilterAudioProcessor::getName() const
{
    return JucePlugin_Name;
}

int _1f_ilterAudioProcessor::getNumParameters()
{
    return 2;
}

float _1f_ilterAudioProcessor::getParameter (int index)
{
    // This method will be called by the host, probably on the audio thread, so
    // it's absolutely time-critical. Don't use critical sections or anything
    // UI-related, or anything at all that may block in any way!
    switch (index)
    {
        case gainParam:     return gain;
        case delayParam:    return delay;
        default:            return 0.0f;
    }
}

void _1f_ilterAudioProcessor::setParameter (int index, float newValue)
{
    // This method will be called by the host, probably on the audio thread, so
    // it's absolutely time-critical. Don't use critical sections or anything
    // UI-related, or anything at all that may block in any way!
    switch (index)
    {
        case gainParam:     gain = newValue;  break;
        case delayParam:    delay = newValue;  break;
        default:            break;
    }
}

const String _1f_ilterAudioProcessor::getParameterName (int index)
{
    switch (index)
    {
        case gainParam:     return "Output Gain";
        case delayParam:    return "Filter Cutoff";
        default:            break;
    }
    
    return String::empty;
}

const String _1f_ilterAudioProcessor::getParameterText (int index)
{
    return String (getParameter (index), 2);
}

const String _1f_ilterAudioProcessor::getInputChannelName (int channelIndex) const
{
    return String (channelIndex + 1);
}

const String _1f_ilterAudioProcessor::getOutputChannelName (int channelIndex) const
{
    return String (channelIndex + 1);
}

bool _1f_ilterAudioProcessor::isInputChannelStereoPair (int index) const
{
    return true;
}

bool _1f_ilterAudioProcessor::isOutputChannelStereoPair (int index) const
{
    return true;
}

bool _1f_ilterAudioProcessor::acceptsMidi() const
{
   #if JucePlugin_WantsMidiInput
    return true;
   #else
    return false;
   #endif
}

bool _1f_ilterAudioProcessor::producesMidi() const
{
   #if JucePlugin_ProducesMidiOutput
    return true;
   #else
    return false;
   #endif
}

bool _1f_ilterAudioProcessor::silenceInProducesSilenceOut() const
{
    return false;
}

double _1f_ilterAudioProcessor::getTailLengthSeconds() const
{
    return 0.0;
}

int _1f_ilterAudioProcessor::getNumPrograms()
{
    return 0;
}

int _1f_ilterAudioProcessor::getCurrentProgram()
{
    return 0;
}

void _1f_ilterAudioProcessor::setCurrentProgram (int index)
{
}

const String _1f_ilterAudioProcessor::getProgramName (int index)
{
    return String::empty;
}

void _1f_ilterAudioProcessor::changeProgramName (int index, const String& newName)
{
}

//==============================================================================
void _1f_ilterAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    // Use this method as the place to do any pre-playback
    // initialisation that you need..
    delayBuffer.clear();
    
}

void _1f_ilterAudioProcessor::releaseResources()
{
    // When playback stops, you can use this as an opportunity to free up any
    // spare memory, etc.
}


void _1f_ilterAudioProcessor::processBlock (AudioSampleBuffer& buffer, MidiBuffer& midiMessages)
{
    // This is the place where you'd normally do the guts of your plugin's
    // audio processing...
    const int numSamples = buffer.getNumSamples();
    int channel;
    int dp = delayPosition;
    
    
    const double coefficients1[4] = {3.9418652031, -5.8304296418, 3.8351221403, -0.9465605711};  //400Hz
    
    const double coefficients2[4] = {3.9263413498, -5.7866072422, 3.7939131077, -0.9336541739};  //500Hz

    
    double coefficientsCURRENT[4] = {(coefficients1[0]*delay + coefficients2[0]*(1-delay)),
                                    (coefficients1[1]*delay + coefficients2[1]*(1-delay)),
                                    (coefficients1[2]*delay + coefficients2[2]*(1-delay)),
                                    (coefficients1[3]*delay + coefficients2[3]*(1-delay))};
    
    
    double filterGain = 1 - (coefficientsCURRENT[0]
                           + coefficientsCURRENT[1]
                           + coefficientsCURRENT[2]
                           + coefficientsCURRENT[3]);
    
    
    // Go through the incoming data, and apply our gain to it...
    for (channel = 0; channel < getNumInputChannels(); ++channel)
        buffer.applyGain (channel, 0, buffer.getNumSamples(), gain);
    
    
    
    // Apply our filter to the new output...
    for (channel = 0; channel < getNumInputChannels(); ++channel)
    {
        float* channelData = buffer.getSampleData (channel);
        float* delayData = delayBuffer.getSampleData (jmin (channel, delayBuffer.getNumChannels() - 1));
        dp = delayPosition;
        
        for (int i = 0; i < numSamples; i++)
        {
            channelData[i] = channelData[i] * filterGain
                            + coefficientsCURRENT[0]*delayData[(dp + 4) % 5]  //There are a lot of constants and I feel bad about that.
                            + coefficientsCURRENT[1]*delayData[(dp + 3) % 5]
                            + coefficientsCURRENT[2]*delayData[(dp + 2) % 5]
                            + coefficientsCURRENT[3]*delayData[(dp + 1) % 5];
            
            delayData[dp] = channelData[i];
            if (++dp >= delayBuffer.getNumSamples())  //I don't like the mutation that does but I also don't want to change things that appear to work.
                dp = 0;
        }
    }
    
    delayPosition = dp;

    // In case we have more outputs than inputs, we'll clear any output
    // channels that didn't contain input data, (because these aren't
    // guaranteed to be empty - they may contain garbage).
    for (int i = getNumInputChannels(); i < getNumOutputChannels(); ++i)
    {
        buffer.clear (i, 0, buffer.getNumSamples());
    }
}

//==============================================================================
bool _1f_ilterAudioProcessor::hasEditor() const
{
    return true; // (change this to false if you choose to not supply an editor)
}

AudioProcessorEditor* _1f_ilterAudioProcessor::createEditor()
{
    return new _1f_ilterAudioProcessorEditor (this);
}

//==============================================================================
void _1f_ilterAudioProcessor::getStateInformation (MemoryBlock& destData)
{
    // You should use this method to store your parameters in the memory block.
    // You could do that either as raw data, or use the XML or ValueTree classes
    // as intermediaries to make it easy to save and load complex data.
}

void _1f_ilterAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    // You should use this method to restore your parameters from this memory block,
    // whose contents will have been created by the getStateInformation() call.
}

//==============================================================================
// This creates new instances of the plugin..
AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new _1f_ilterAudioProcessor();
}
