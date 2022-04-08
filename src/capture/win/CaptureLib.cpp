#include <windows.h>
#include <dshow.h>
#include <iostream>
#include <string.h>

using std::string;
using std::wstring;

extern "C" {
    __declspec(dllexport) const char* ListDevices();
}

HRESULT EnumerateDevices(REFGUID category, IEnumMoniker **ppEnum) {
    // Create the System Device Enumerator.

    HRESULT hr;
    ICreateDevEnum *pDevEnum = NULL;
    hr = CoCreateInstance(CLSID_SystemDeviceEnum, NULL, CLSCTX_INPROC_SERVER,
                          IID_ICreateDevEnum, (void **)&pDevEnum);

    if (SUCCEEDED(hr)) {
        // Create an enumerator for the category.
        hr = pDevEnum->CreateClassEnumerator(category, ppEnum, 0);
        if (hr == S_FALSE) {
            hr = VFW_E_NOT_FOUND; // The category is empty. Treat as an error.
        }
        pDevEnum->Release();
    }
    return hr;
}

const char* ListDevices() {
    string devices = "";
    
    HRESULT hr = CoInitializeEx(NULL, COINIT_MULTITHREADED);

    if (SUCCEEDED(hr)) {
        IEnumMoniker *pEnum;

        hr = EnumerateDevices(CLSID_VideoInputDeviceCategory, &pEnum);
        if (SUCCEEDED(hr)) {
            IMoniker *pMoniker = NULL;

            while (pEnum->Next(1, &pMoniker, NULL) == S_OK) {
                IPropertyBag *pPropBag;
                HRESULT hr = pMoniker->BindToStorage(0, 0, IID_PPV_ARGS(&pPropBag));
                
                if (FAILED(hr)) {
                    pMoniker->Release();
                    continue;
                }

                VARIANT var;
                VariantInit(&var);

                hr = pPropBag->Read(L"Description", &var, 0);
                if (FAILED(hr)) {
                    hr = pPropBag->Read(L"FriendlyName", &var, 0);
                }

                if (SUCCEEDED(hr)) {
                    if (devices.size() > 0) {
                        devices += "\n";
                    }
                    wstring ws(var.bstrVal, SysStringLen(var.bstrVal));;
                    string new_device(ws.begin(), ws.end());
                    devices += new_device;
                    VariantClear(&var);
                }

                pPropBag->Release();
                pMoniker->Release();
            }
            pEnum->Release();
        }
        CoUninitialize();
    }

    char* char_devices = &devices[0];
    return char_devices;
}